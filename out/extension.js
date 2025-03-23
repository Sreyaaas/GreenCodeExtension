"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.deactivate = exports.activate = void 0;
const vscode = __importStar(require("vscode"));
const child_process_1 = require("child_process");
const path = __importStar(require("path"));
function activate(context) {
    console.log('Green Code is now active!');
    // Register command to analyze current file
    let analyzeCurrentFileCmd = vscode.commands.registerCommand('green-code.analyzeCurrentFile', async () => {
        const editor = vscode.window.activeTextEditor;
        if (!editor) {
            vscode.window.showErrorMessage('No active editor found');
            return;
        }
        const document = editor.document;
        if (document.languageId !== 'python') {
            vscode.window.showInformationMessage('Green Code analysis only works on Python files');
            return;
        }
        if (document.isDirty) {
            await document.save();
        }
        const filePath = document.fileName;
        // Show progress notification
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing code for sustainability",
            cancellable: false
        }, async (progress) => {
            progress.report({ increment: 0 });
            try {
                // Run the Python script
                const result = await runPythonAnalysis(filePath);
                progress.report({ increment: 100 });
                // Show success message
                vscode.window.showInformationMessage(`Sustainability analysis complete: ${result}`);
                // Refresh the editor content
                await vscode.commands.executeCommand('workbench.action.files.revert');
            }
            catch (error) {
                vscode.window.showErrorMessage(`Analysis failed: ${error}`);
            }
            return Promise.resolve();
        });
    });
    // Register command to analyze all Python files in workspace
    let analyzeWorkspaceCmd = vscode.commands.registerCommand('green-code.analyzeWorkspace', async () => {
        const workspaceFolders = vscode.workspace.workspaceFolders;
        if (!workspaceFolders) {
            vscode.window.showErrorMessage('No workspace folder open');
            return;
        }
        vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: "Analyzing workspace for sustainability",
            cancellable: true
        }, async (progress, token) => {
            const pythonFiles = await vscode.workspace.findFiles('**/*.py', '**/node_modules/**');
            let processedCount = 0;
            for (const file of pythonFiles) {
                if (token.isCancellationRequested) {
                    break;
                }
                try {
                    await runPythonAnalysis(file.fsPath);
                    processedCount++;
                    progress.report({
                        increment: (100 / pythonFiles.length),
                        message: `Processed ${processedCount}/${pythonFiles.length} files`
                    });
                }
                catch (error) {
                    vscode.window.showWarningMessage(`Failed to analyze ${file.fsPath}: ${error}`);
                }
            }
            vscode.window.showInformationMessage(`Sustainability analysis complete for ${processedCount} files`);
            return Promise.resolve();
        });
    });
    // Register command to configure API key
    let configureApiKeyCmd = vscode.commands.registerCommand('green-code.configureApiKey', async () => {
        const apiKey = await vscode.window.showInputBox({
            prompt: 'Enter your Groq API key',
            password: true
        });
        if (apiKey) {
            await vscode.workspace.getConfiguration().update('greenCode.apiKey', apiKey, true);
            vscode.window.showInformationMessage('Groq API key saved');
        }
    });
    // Register event handler for file save if auto-analyze is enabled
    let onSaveHandler = vscode.workspace.onDidSaveTextDocument((document) => {
        if (document.languageId === 'python' &&
            vscode.workspace.getConfiguration('greenCode').get('autoAnalyzeOnSave')) {
            vscode.commands.executeCommand('green-code.analyzeCurrentFile');
        }
    });
    context.subscriptions.push(analyzeCurrentFileCmd, analyzeWorkspaceCmd, configureApiKeyCmd, onSaveHandler);
}
exports.activate = activate;
async function runPythonAnalysis(filePath) {
    const pythonPath = vscode.workspace.getConfiguration('python').get('pythonPath') || 'python';
    const extensionPath = vscode.extensions.getExtension('your-publisher-name.green-code')?.extensionPath;
    if (!extensionPath) {
        throw new Error('Could not find extension path');
    }
    const scriptPath = path.join(extensionPath, 'main.py');
    // Check if the API key is configured in VS Code settings
    const apiKey = vscode.workspace.getConfiguration('greenCode').get('apiKey');
    return new Promise((resolve, reject) => {
        let env = Object.assign({}, process.env);
        if (apiKey) {
            env.GROQ_API_KEY = apiKey;
        }
        (0, child_process_1.exec)(`"${pythonPath}" "${scriptPath}" "${filePath}"`, { env }, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
                return;
            }
            resolve(stdout.trim());
        });
    });
}
function deactivate() { }
exports.deactivate = deactivate;
//# sourceMappingURL=extension.js.map