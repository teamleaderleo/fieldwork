// Copyright 2019-2024 Tauri Programme within The Commons Conservancy
// SPDX-License-Identifier: Apache-2.0
// SPDX-License-Identifier: MIT

;(function () {
  /**
   * A runtime generated key to ensure an IPC call comes from an initialized frame.
   *
   * This is declared outside the `window.__TAURI_INVOKE__` definition to prevent
   * the key from being leaked by `window.__TAURI_INVOKE__.toString()`.
   */
  const __TAURI_INVOKE_KEY__ = __TEMPLATE_invoke_key__

  const processIpcMessage = __RAW_process_ipc_message_fn__
  const osName = __TEMPLATE_os_name__
  const fetchChannelDataCommand = __TEMPLATE_fetch_channel_data_command__

  // Android cannot read custom-protocol request bodies for regular commands, but
  // it still uses the custom protocol to fetch large channel responses.
  const canUseCustomProtocol = osName !== 'android'

  let customProtocolState = 'unknown'
  let customProtocolProbe = null
  let channelCustomProtocolState = 'unknown'
  let channelCustomProtocolProbe = null

  function getPayloadContentType(payload) {
    return payload instanceof ArrayBuffer
      || ArrayBuffer.isView(payload)
      || Array.isArray(payload)
      ? 'application/octet-stream'
      : 'application/json'
  }

  function getIpcHeaders(message, contentType) {
    const { callback, error, options } = message
    const headers = new Headers((options && options.headers) || {})
    headers.set('Content-Type', contentType)
    headers.set('Tauri-Callback', callback)
    headers.set('Tauri-Error', error)
    headers.set('Tauri-Invoke-Key', __TAURI_INVOKE_KEY__)
    return headers
  }

  function getIpcRequest(message) {
    const { contentType, data } = processIpcMessage(message.payload)
    return {
      data,
      headers: getIpcHeaders(message, contentType)
    }
  }

  function sendPostMessage(message, customProtocolIpcBlocked) {
    const { cmd, callback, error, payload, options } = message
    const headers = Object.fromEntries(
      new Headers((options && options.headers) || {}).entries()
    )
    const { data } = processIpcMessage({
      cmd,
      callback,
      error,
      options: {
        ...options,
        headers,
        customProtocolIpcBlocked
      },
      payload,
      __TAURI_INVOKE_KEY__
    })
    // `window.ipc.postMessage` came from `tauri-runtime-wry` > `wry` `with_ipc_handler`.
    window.ipc.postMessage(data)
  }

  function probeCustomProtocol(message, channelOnly) {
    const state = channelOnly
      ? channelCustomProtocolState
      : customProtocolState
    if (state !== 'unknown') {
      return Promise.resolve(state === 'available')
    }

    const pendingProbe = channelOnly
      ? channelCustomProtocolProbe
      : customProtocolProbe
    if (pendingProbe) {
      return pendingProbe
    }

    // Do not serialize the payload for the capability probe. Serialization can
    // call user-defined __TAURI_TO_IPC_KEY__ hooks and must happen exactly once
    // for the transport that actually dispatches the command.
    const headers = getIpcHeaders(
      message,
      getPayloadContentType(message.payload)
    )
    const probe = fetch(
      window.__TAURI_INTERNALS__.convertFileSrc(message.cmd, 'ipc'),
      { method: 'HEAD', headers }
    ).then(
      () => {
        if (channelOnly) {
          channelCustomProtocolState = 'available'
        } else {
          customProtocolState = 'available'
        }
        return true
      },
      () => {
        if (channelOnly) {
          channelCustomProtocolState = 'blocked'
        } else {
          customProtocolState = 'blocked'
        }
        return false
      }
    )

    if (channelOnly) {
      channelCustomProtocolProbe = probe
    } else {
      customProtocolProbe = probe
    }
    return probe
  }

  function sendCustomProtocol(message, channelOnly) {
    const { cmd, callback, error } = message
    const { data, headers } = getIpcRequest(message)

    fetch(window.__TAURI_INTERNALS__.convertFileSrc(cmd, 'ipc'), {
      method: 'POST',
      body: data,
      headers
    })
      .then((response) => {
        const callbackId =
          response.headers.get('Tauri-Response') === 'ok' ? callback : error
        // we need to split here because on Android the content-type gets duplicated
        switch ((response.headers.get('content-type') || '').split(',')[0]) {
          case 'application/json':
            return response.json().then((r) => [callbackId, r])
          case 'text/plain':
            return response.text().then((r) => [callbackId, r])
          default:
            return response.arrayBuffer().then((r) => [callbackId, r])
        }
      })
      .then(
        ([callbackId, data]) => {
          window.__TAURI_INTERNALS__.runCallback(callbackId, data)
        },
        (e) => {
          console.warn(
            'IPC custom protocol failed; future invokes will use the postMessage interface',
            e
          )
          if (channelOnly) {
            channelCustomProtocolState = 'blocked'
          } else {
            customProtocolState = 'blocked'
          }
          // This POST may already have dispatched a command. Reject this invoke
          // instead of replaying it through a second transport.
          window.__TAURI_INTERNALS__.runCallback(error, e)
        }
      )
  }

  function sendIpcMessage(message) {
    if (!canUseCustomProtocol) {
      if (message.cmd !== fetchChannelDataCommand) {
        sendPostMessage(message, channelCustomProtocolState === 'blocked')
        return
      }

      if (channelCustomProtocolState === 'unknown') {
        probeCustomProtocol(message, true).then(() => sendIpcMessage(message))
        return
      }

      if (channelCustomProtocolState === 'available') {
        sendCustomProtocol(message, true)
      } else {
        sendPostMessage(message, true)
      }
      return
    }

    if (customProtocolState === 'unknown') {
      probeCustomProtocol(message, false).then(() => sendIpcMessage(message))
      return
    }

    if (customProtocolState === 'available') {
      sendCustomProtocol(message, false)
    } else {
      sendPostMessage(message, true)
    }
  }

  Object.defineProperty(window.__TAURI_INTERNALS__, 'postMessage', {
    value: sendIpcMessage
  })
})()
