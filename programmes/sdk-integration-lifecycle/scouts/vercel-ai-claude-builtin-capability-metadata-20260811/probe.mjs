#!/usr/bin/env node

// Source model for vercel/ai at cfc587bdfd8fd1996dd902edd14143be6e034baf.
// This intentionally copies only the small tables/functions needed to distinguish
// capability-classification and filtering hypotheses. It is not target-native
// execution and must not be presented as such.

const catalogKinds = {
  PowerShell: 'bash',
  ListMcpResourcesTool: 'readonly',
  ReadMcpResourceTool: 'readonly',
  EnterPlanMode: 'readonly',
  LSP: 'readonly',
  ReportFindings: 'readonly',
  CronList: 'readonly',
  WaitForMcpServers: 'readonly',
  SendUserFile: 'readonly',
  DesignSync: 'edit',
  RemoteTrigger: 'edit',
};

const nativeToolKinds = {
  Read: 'readonly',
  Glob: 'readonly',
  Grep: 'readonly',
  WebSearch: 'readonly',
  WebFetch: 'readonly',
  TaskGet: 'readonly',
  TaskList: 'readonly',
  TaskOutput: 'readonly',
  ListMcpResources: 'readonly',
  ReadMcpResource: 'readonly',
  Write: 'edit',
  Edit: 'edit',
  NotebookEdit: 'edit',
  TodoWrite: 'edit',
  TaskCreate: 'edit',
  TaskUpdate: 'edit',
  TaskStop: 'edit',
  EnterWorktree: 'edit',
  ExitWorktree: 'edit',
  ExitPlanMode: 'edit',
  Skill: 'readonly',
  AskUserQuestion: 'readonly',
  ToolSearch: 'readonly',
  Bash: 'bash',
  Monitor: 'bash',
};

function nativeToolRequiresApproval(nativeName, permissionMode) {
  if (permissionMode === 'allow-all') return false;
  const kind = nativeToolKinds[nativeName] ?? 'edit';
  if (permissionMode === 'allow-edits') return kind === 'bash';
  return kind === 'edit' || kind === 'bash';
}

const publicToNative = {
  read: 'Read',
  write: 'Write',
  edit: 'Edit',
  bash: 'Bash',
  glob: 'Glob',
  grep: 'Grep',
  webSearch: 'WebSearch',
  WebFetch: 'WebFetch',
  NotebookEdit: 'NotebookEdit',
  TodoWrite: 'TodoWrite',
  Agent: 'Agent',
  TaskCreate: 'TaskCreate',
  TaskGet: 'TaskGet',
  TaskUpdate: 'TaskUpdate',
  TaskList: 'TaskList',
  TaskStop: 'TaskStop',
  TaskOutput: 'TaskOutput',
  Monitor: 'Monitor',
  ListMcpResources: 'ListMcpResources',
  ReadMcpResource: 'ReadMcpResource',
  ExitPlanMode: 'ExitPlanMode',
  EnterWorktree: 'EnterWorktree',
  ExitWorktree: 'ExitWorktree',
  AskUserQuestion: 'AskUserQuestion',
  Skill: 'Skill',
  ToolSearch: 'ToolSearch',
};

const publicToolNames = Object.keys(publicToNative);
const toNativeName = toolName => publicToNative[toolName] ?? toolName;

function resolveInactiveNativeTools(toolFiltering) {
  if (toolFiltering == null) return [];
  const inactiveToolNames =
    toolFiltering.mode === 'allow'
      ? publicToolNames.filter(name => !toolFiltering.toolNames.includes(name))
      : toolFiltering.toolNames;
  return inactiveToolNames.map(toNativeName);
}

const permissionRows = Object.entries(catalogKinds).map(([name, catalogKind]) => ({
  name,
  catalogKind,
  bridgeKind: nativeToolKinds[name] ?? '(fallback edit)',
  allowEditsApproval: nativeToolRequiresApproval(name, 'allow-edits'),
  allowReadsApproval: nativeToolRequiresApproval(name, 'allow-reads'),
}));

const allowReadComplement = resolveInactiveNativeTools({
  mode: 'allow',
  toolNames: ['read'],
});

const output = {
  targetRevision: 'cfc587bdfd8fd1996dd902edd14143be6e034baf',
  permissionRows,
  filtering: {
    allowReadComplement: {
      count: allowReadComplement.length,
      containsPowerShell: allowReadComplement.includes('PowerShell'),
      containsWorkflow: allowReadComplement.includes('Workflow'),
    },
    explicitDenyPowerShell: resolveInactiveNativeTools({
      mode: 'deny',
      toolNames: ['PowerShell'],
    }),
  },
};

process.stdout.write(`${JSON.stringify(output, null, 2)}\n`);
