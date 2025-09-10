import * as vscode from 'vscode';
import { AicacheClient } from './aicacheClient';
import { CachePanelViewProvider } from './cachePanelViewProvider';
import { TeamPresenceViewProvider } from './teamPresenceViewProvider';

let aicacheClient: AicacheClient | undefined;

export async function activate(context: vscode.ExtensionContext) {
	// Get configuration
	const config = vscode.workspace.getConfiguration('aicache');
	const enabled = config.get<boolean>('enabled', true);
	
	if (!enabled) {
		console.log('aicache extension is disabled');
		return;
	}
	
	console.log('aicache extension is activating');
	
	// Initialize aicache client
	const serviceUrl = config.get<string>('serviceUrl', 'http://localhost:8080');
	aicacheClient = new AicacheClient(serviceUrl);
	
	try {
		await aicacheClient.initialize();
		console.log('aicache client initialized successfully');
	} catch (error) {
		console.error('Failed to initialize aicache client:', error);
		vscode.window.showErrorMessage('Failed to connect to aicache service');
		return;
	}
	
	// Register commands
	const queryCacheCommand = vscode.commands.registerCommand('aicache.queryCache', async () => {
		if (!aicacheClient) {
			vscode.window.showErrorMessage('aicache client not initialized');
			return;
		}
		
		try {
			const editor = vscode.window.activeTextEditor;
			if (!editor) {
				vscode.window.showErrorMessage('No active editor found');
				return;
			}
			
			// Get selected text or current line
			const selection = editor.selection;
			let query = '';
			
			if (!selection.isEmpty) {
				query = editor.document.getText(selection);
			} else {
				const line = editor.document.lineAt(editor.selection.active.line);
				query = line.text.trim();
			}
			
			if (!query) {
				query = await vscode.window.showInputBox({
					prompt: 'Enter your query',
					placeHolder: 'e.g., How to implement authentication in Flask?'
				}) || '';
			}
			
			if (query) {
				const response = await aicacheClient.queryCache(query, getContext(editor));
				if (response) {
					vscode.window.showInformationMessage(response);
				}
			}
		} catch (error) {
			console.error('Error querying cache:', error);
			vscode.window.showErrorMessage('Failed to query cache: ' + (error as Error).message);
		}
	});
	
	const showCachePanelCommand = vscode.commands.registerCommand('aicache.showCachePanel', () => {
		vscode.commands.executeCommand('aicache.cachePanel.focus');
	});
	
	const refreshCacheCommand = vscode.commands.registerCommand('aicache.refreshCache', async () => {
		if (!aicacheClient) {
			vscode.window.showErrorMessage('aicache client not initialized');
			return;
		}
		
		try {
			await aicacheClient.refreshCache();
			vscode.window.showInformationMessage('Cache refreshed successfully');
		} catch (error) {
			console.error('Error refreshing cache:', error);
			vscode.window.showErrorMessage('Failed to refresh cache: ' + (error as Error).message);
		}
	});
	
	// Register view providers
	const cachePanelViewProvider = new CachePanelViewProvider(context.extensionUri, aicacheClient);
	const teamPanelViewProvider = new TeamPresenceViewProvider(context.extensionUri, aicacheClient);
	
	context.subscriptions.push(
		queryCacheCommand,
		showCachePanelCommand,
		refreshCacheCommand,
		vscode.window.registerWebviewViewProvider('aicache.cachePanel', cachePanelViewProvider),
		vscode.window.registerWebviewViewProvider('aicache.teamPanel', teamPanelViewProvider)
	);
	
	// Update status bar
	const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Right, 100);
	statusBarItem.text = '$(database) aicache';
	statusBarItem.tooltip = 'aicache is active';
	statusBarItem.command = 'aicache.showCachePanel';
	statusBarItem.show();
	context.subscriptions.push(statusBarItem);
	
	console.log('aicache extension activated successfully');
}

export function deactivate() {
	console.log('aicache extension deactivated');
}

function getContext(editor: vscode.TextEditor): any {
	const document = editor.document;
	const languageId = document.languageId;
	const fileName = document.fileName;
	const workspaceFolder = vscode.workspace.getWorkspaceFolder(document.uri)?.name || '';
	
	return {
		language: languageId,
		fileName: fileName,
		workspace: workspaceFolder,
		line: editor.selection.active.line,
		character: editor.selection.active.character
	};
}