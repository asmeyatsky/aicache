import axios, { AxiosInstance } from 'axios';

export interface CacheQueryResponse {
	prompt: string;
	response: string;
	context: any;
	timestamp: number;
	cacheType: string;
}

export interface CacheEntry {
	cacheKey: string;
	prompt: string;
	createdAt: number;
	accessCount: number;
	tags: string[];
}

export interface TeamMember {
	userId: string;
	username: string;
	status: string;
	currentProject: string;
	currentTask: string;
	lastActive: number;
}

export class AicacheClient {
	private client: AxiosInstance;
	private initialized: boolean = false;
	
	constructor(private serviceUrl: string) {
		this.client = axios.create({
			baseURL: serviceUrl,
			timeout: 10000,
		});
	}
	
	async initialize(): Promise<void> {
		try {
			// Test connection
			await this.client.get('/health');
			this.initialized = true;
		} catch (error) {
			throw new Error(`Failed to connect to aicache service at ${this.serviceUrl}: ${error}`);
		}
	}
	
	async queryCache(prompt: string, context: any): Promise<string | null> {
		if (!this.initialized) {
			throw new Error('Client not initialized');
		}
		
		try {
			const response = await this.client.post<CacheQueryResponse>('/cache/query', {
				prompt,
				context
			});
			
			return response.data.response;
		} catch (error) {
			console.error('Cache query failed:', error);
			return null;
		}
	}
	
	async setCache(prompt: string, response: string, context: any): Promise<string> {
		if (!this.initialized) {
			throw new Error('Client not initialized');
		}
		
		try {
			const result = await this.client.post<{ cacheKey: string }>('/cache/set', {
				prompt,
				response,
				context
			});
			
			return result.data.cacheKey;
		} catch (error) {
			console.error('Cache set failed:', error);
			throw error;
		}
	}
	
	async listCacheEntries(): Promise<CacheEntry[]> {
		if (!this.initialized) {
			throw new Error('Client not initialized');
		}
		
		try {
			const response = await this.client.get<CacheEntry[]>('/cache/list');
			return response.data;
		} catch (error) {
			console.error('Cache list failed:', error);
			return [];
		}
	}
	
	async getTeamPresence(): Promise<TeamMember[]> {
		if (!this.initialized) {
			throw new Error('Client not initialized');
		}
		
		try {
			const response = await this.client.get<TeamMember[]>('/team/presence');
			return response.data;
		} catch (error) {
			console.error('Team presence query failed:', error);
			return [];
		}
	}
	
	async refreshCache(): Promise<void> {
		if (!this.initialized) {
			throw new Error('Client not initialized');
		}
		
		try {
			await this.client.post('/cache/refresh');
		} catch (error) {
			console.error('Cache refresh failed:', error);
			throw error;
		}
	}
	
	isInitialized(): boolean {
		return this.initialized;
	}
}