function mergeDeep(target, source) {
  const out = { ...target };
  for (const [key, value] of Object.entries(source)) {
    if (
      value &&
      typeof value === 'object' &&
      !Array.isArray(value) &&
      out[key] &&
      typeof out[key] === 'object' &&
      !Array.isArray(out[key])
    ) {
      out[key] = mergeDeep(out[key], value);
    } else {
      out[key] = value;
    }
  }
  return out;
}

const projectConfig = {
  mcp: {
    'repo-owned': {
      type: 'local',
      enabled: true,
      command: ['node', 'repo-mcp.mjs'],
    },
  },
};

const providerConfig = {
  provider: {
    openai: {
      options: { apiKey: 'probe-openai-secret' },
    },
  },
  mcp: {
    'caller-owned': {
      type: 'remote',
      url: 'https://example.invalid/mcp',
    },
  },
};

// Pinned OpenCode loads project config first, then merges
// OPENCODE_CONFIG_CONTENT. This dependency-free helper models the object merge
// for the nested fields exercised by the probe; it is evidence about the
// source-level mechanism, not a target-executed OpenCode run.
const effectiveConfig = mergeDeep(projectConfig, providerConfig);

// createOpencodeServer inherits process.env and writes provider config into
// OPENCODE_CONFIG_CONTENT. OpenCode connectLocal then inherits process.env into
// a repo-configured MCP subprocess.
const openCodeServerEnv = {
  OPENAI_API_KEY: 'probe-openai-secret',
  OPENCODE_CONFIG_CONTENT: JSON.stringify(providerConfig),
};
const repoMcpEnv = {
  ...openCodeServerEnv,
  ...(effectiveConfig.mcp['repo-owned'].environment ?? {}),
};

const result = {
  repoMcpSurvivesConfigMerge: Boolean(effectiveConfig.mcp['repo-owned']),
  callerMcpAlsoPresent: Boolean(effectiveConfig.mcp['caller-owned']),
  repoMcpReceivesDirectProviderCredential:
    repoMcpEnv.OPENAI_API_KEY === 'probe-openai-secret',
  repoMcpReceivesSerializedProviderCredential:
    repoMcpEnv.OPENCODE_CONFIG_CONTENT.includes('probe-openai-secret'),
};

for (const [name, ok] of Object.entries(result)) {
  if (!ok) throw new Error(`probe failed: ${name}`);
}

console.log(JSON.stringify(result, null, 2));
