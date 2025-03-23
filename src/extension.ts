import * as vscode from 'vscode';
import { exec } from 'child_process';
import * as path from 'path';
import * as fs from 'fs';


export function activate(context: vscode.ExtensionContext) {
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
            } catch (error) {
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
                } catch (error) {
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

async function runPythonAnalysis(filePath: string): Promise<string> {
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
            env.GROQ_API_KEY = apiKey as string;
        }
        
        exec(`"${pythonPath}" "${scriptPath}" "${filePath}"`, { env }, (error, stdout, stderr) => {
            if (error) {
                reject(stderr || error.message);
                return;
            }
            resolve(stdout.trim());
        });
    });
}

export function deactivate() {}