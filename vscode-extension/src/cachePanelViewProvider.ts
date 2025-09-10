import * as vscode from 'vscode';
import { AicacheClient, CacheEntry } from './aicacheClient';

export class CachePanelViewProvider implements vscode.WebviewViewProvider {
	public static readonly viewType = 'aicache.cachePanel';
	
	private _view?: vscode.WebviewView;
	private _cachedEntries: CacheEntry[] = [];
	
	constructor(
		private readonly _extensionUri: vscode.Uri,
		private readonly _aicacheClient: AicacheClient
	) { }
	
	public resolveWebviewView(
		webviewView: vscode.WebviewView,
		context: vscode.WebviewViewResolveContext,
		_token: vscode.CancellationToken,
	) {
		this._view = webviewView;
		
		webviewView.webview.options = {
			enableScripts: true,
			localResourceRoots: [
				this._extensionUri
			]
		};
		
		webviewView.webview.html = this._getHtmlForWebview(webviewView.webview);
		
		// Set up message passing
		webviewView.webview.onDidReceiveMessage(
			message => {
				switch (message.command) {
					case 'refresh':
						this._refreshCacheEntries();
						break;
					case 'query':
						this._queryCacheEntry(message.cacheKey);
						break;
				}
			},
			undefined,
			[]
		);
		
		// Load initial data
		this._refreshCacheEntries();
	}
	
	private async _refreshCacheEntries() {
		if (!this._view) {
			return;
		}
		
		try {
			this._cachedEntries = await this._aicacheClient.listCacheEntries();
			this._updateWebview();
		} catch (error) {
			console.error('Failed to refresh cache entries:', error);
			this._view.webview.postMessage({
				command: 'error',
				message: 'Failed to load cache entries'
			});
		}
	}
	
	private async _queryCacheEntry(cacheKey: string) {
		// This would typically open the cache entry in a new editor
		vscode.window.showInformationMessage(`Querying cache entry: ${cacheKey}`);
	}
	
	private _updateWebview() {
		if (!this._view) {
			return;
		}
		
		this._view.webview.postMessage({
			command: 'updateEntries',
			entries: this._cachedEntries
		});
	}
	
	private _getHtmlForWebview(webview: vscode.Webview) {
		// Local path to main script run in the webview
		const scriptUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.js'));
		
		// Uri to load styles into webview
		const styleResetUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'reset.css'));
		const styleVSCodeUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'vscode.css'));
		const styleMainUri = webview.asWebviewUri(vscode.Uri.joinPath(this._extensionUri, 'media', 'main.css'));
		
		// Use a nonce to only allow specific scripts to be run
		const nonce = getNonce();
		
		return `<!DOCTYPE html>
			<html lang="en">
			<head>
				<meta charset="UTF-8">
				
				<!--
					Use a content security policy to only allow loading styles from our extension directory,
					and only allow scripts that have a specific nonce.
				-->
				<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src ${webview.cspSource}; script-src 'nonce-${nonce}';">
				
				<meta name="viewport" content="width=device-width, initial-scale=1.0">
				
				<link href="${styleResetUri}" rel="stylesheet">
				<link href="${styleVSCodeUri}" rel="stylesheet">
				<link href="${styleMainUri}" rel="stylesheet">
				
				<title>aicache Cache Panel</title>
			</head>
			<body>
				<div class="container">
					<h1>Cache Entries</h1>
					<button id="refresh-button">Refresh</button>
					<div id="entries-container"></div>
				</div>
				
				<script nonce="${nonce}" src="${scriptUri}"></script>
			</body>
			</html>`;
	}
}

function getNonce() {
	let text = '';
	const possible = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
	for (let i = 0; i < 32; i++) {
		text += possible.charAt(Math.floor(Math.random() * possible.length));
	}
	return text;
}