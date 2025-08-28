// GDPR Compliance Framework
// Data processing agreements and compliance management

interface DataProcessingRecord {
  id: string;
  dataController: string;
  dataProcessor: string;
  processingActivities: string[];
  dataCategories: string[];
  dataSubjects: string[];
  processingPurposes: string[];
  retentionPeriod: string;
  securityMeasures: string[];
  subProcessors: string[];
  createdAt: string;
  updatedAt: string;
}

interface DataSubjectRequest {
  id: string;
  type: 'access' | 'rectification' | 'erasure' | 'restriction' | 'portability' | 'objection';
  dataSubjectId: string;
  status: 'pending' | 'processing' | 'completed' | 'rejected';
  requestData: any;
  response?: string;
  createdAt: string;
  resolvedAt?: string;
}

interface DataBreachRecord {
  id: string;
  description: string;
  affectedDataSubjects: number;
  affectedDataCategories: string[];
  breachType: 'confidentiality' | 'integrity' | 'availability';
  discoveredAt: string;
  reportedToSupervisorAt?: string;
  reportedToDataSubjectsAt?: string;
  remedialActions: string[];
  status: 'contained' | 'investigating' | 'resolved';
}

class GDPRComplianceManager {
  private static instance: GDPRComplianceManager;
  private processingRecords: DataProcessingRecord[] = [];
  private subjectRequests: DataSubjectRequest[] = [];
  private breachRecords: DataBreachRecord[] = [];

  private constructor() {
    // Initialize with mock data for demonstration
    this.initializeMockData();
  }

  // Singleton pattern
  public static getInstance(): GDPRComplianceManager {
    if (!GDPRComplianceManager.instance) {
      GDPRComplianceManager.instance = new GDPRComplianceManager();
    }
    return GDPRComplianceManager.instance;
  }

  // Initialize mock data
  private initializeMockData() {
    this.processingRecords = [
      {
        id: 'dpr_001',
        dataController: 'Acme Corporation',
        dataProcessor: 'ReliQuary Inc.',
        processingActivities: [
          'Storage of user profile data',
          'Processing of API requests',
          'Generation of usage analytics'
        ],
        dataCategories: [
          'Identity data',
          'Contact data',
          'Technical data',
          'Usage data'
        ],
        dataSubjects: [
          'Employees',
          'Customers',
          'Website visitors'
        ],
        processingPurposes: [
          'Provision of services',
          'Performance of contract',
          'Legitimate interests'
        ],
        retentionPeriod: '2 years from last activity',
        securityMeasures: [
          'End-to-end encryption',
          'Access controls',
          'Regular security audits',
          'Post-quantum cryptography'
        ],
        subProcessors: [
          'AWS for cloud infrastructure',
          'Stripe for payment processing'
        ],
        createdAt: '2024-01-01T00:00:00Z',
        updatedAt: '2024-01-01T00:00:00Z'
      }
    ];

    this.subjectRequests = [
      {
        id: 'dsr_001',
        type: 'access',
        dataSubjectId: 'user_12345',
        status: 'completed',
        requestData: {
          userId: 'user_12345',
          requestDate: '2024-01-15T10:30:00Z',
          verificationMethod: 'email confirmation'
        },
        response: 'Data access request fulfilled. Personal data has been provided via secure download link.',
        createdAt: '2024-01-15T10:30:00Z',
        resolvedAt: '2024-01-15T11:45:00Z'
      }
    ];

    this.breachRecords = [
      {
        id: 'dbr_001',
        description: 'Unauthorized access attempt to customer database',
        affectedDataSubjects: 0,
        affectedDataCategories: ['Technical data'],
        breachType: 'confidentiality',
        discoveredAt: '2024-01-10T14:22:00Z',
        reportedToSupervisorAt: '2024-01-10T15:30:00Z',
        remedialActions: [
          'Blocked suspicious IP addresses',
          'Rotated database credentials',
          'Enhanced monitoring on affected systems'
        ],
        status: 'contained'
      }
    ];
  }

  // Create a new data processing record
  async createDataProcessingRecord(record: Omit<DataProcessingRecord, 'id' | 'createdAt' | 'updatedAt'>): Promise<DataProcessingRecord> {
    const newRecord: DataProcessingRecord = {
      id: `dpr_${Date.now()}`,
      ...record,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString()
    };

    this.processingRecords.push(newRecord);
    return newRecord;
  }

  // Get all data processing records
  async getDataProcessingRecords(): Promise<DataProcessingRecord[]> {
    return this.processingRecords;
  }

  // Get data processing record by ID
  async getDataProcessingRecordById(id: string): Promise<DataProcessingRecord | undefined> {
    return this.processingRecords.find(record => record.id === id);
  }

  // Update data processing record
  async updateDataProcessingRecord(id: string, updates: Partial<DataProcessingRecord>): Promise<DataProcessingRecord | null> {
    const index = this.processingRecords.findIndex(record => record.id === id);
    if (index === -1) return null;

    this.processingRecords[index] = {
      ...this.processingRecords[index],
      ...updates,
      updatedAt: new Date().toISOString()
    };

    return this.processingRecords[index];
  }

  // Delete data processing record
  async deleteDataProcessingRecord(id: string): Promise<boolean> {
    const initialLength = this.processingRecords.length;
    this.processingRecords = this.processingRecords.filter(record => record.id !== id);
    return this.processingRecords.length < initialLength;
  }

  // Create a new data subject request
  async createDataSubjectRequest(request: Omit<DataSubjectRequest, 'id' | 'createdAt' | 'status'>): Promise<DataSubjectRequest> {
    const newRequest: DataSubjectRequest = {
      id: `dsr_${Date.now()}`,
      status: 'pending',
      ...request,
      createdAt: new Date().toISOString()
    };

    this.subjectRequests.push(newRequest);
    return newRequest;
  }

  // Get all data subject requests
  async getDataSubjectRequests(): Promise<DataSubjectRequest[]> {
    return this.subjectRequests;
  }

  // Get data subject request by ID
  async getDataSubjectRequestById(id: string): Promise<DataSubjectRequest | undefined> {
    return this.subjectRequests.find(request => request.id === id);
  }

  // Update data subject request status
  async updateDataSubjectRequestStatus(id: string, status: DataSubjectRequest['status'], response?: string): Promise<DataSubjectRequest | null> {
    const index = this.subjectRequests.findIndex(request => request.id === id);
    if (index === -1) return null;

    this.subjectRequests[index] = {
      ...this.subjectRequests[index],
      status,
      response,
      resolvedAt: status === 'completed' || status === 'rejected' ? new Date().toISOString() : undefined,
      updatedAt: new Date().toISOString()
    };

    return this.subjectRequests[index];
  }

  // Create a new data breach record
  async createDataBreachRecord(record: Omit<DataBreachRecord, 'id' | 'discoveredAt' | 'status'>): Promise<DataBreachRecord> {
    const newRecord: DataBreachRecord = {
      id: `dbr_${Date.now()}`,
      status: 'investigating',
      discoveredAt: new Date().toISOString(),
      ...record
    };

    this.breachRecords.push(newRecord);
    return newRecord;
  }

  // Get all data breach records
  async getDataBreachRecords(): Promise<DataBreachRecord[]> {
    return this.breachRecords;
  }

  // Get data breach record by ID
  async getDataBreachRecordById(id: string): Promise<DataBreachRecord | undefined> {
    return this.breachRecords.find(record => record.id === id);
  }

  // Update data breach record
  async updateDataBreachRecord(id: string, updates: Partial<DataBreachRecord>): Promise<DataBreachRecord | null> {
    const index = this.breachRecords.findIndex(record => record.id === id);
    if (index === -1) return null;

    this.breachRecords[index] = {
      ...this.breachRecords[index],
      ...updates
    };

    return this.breachRecords[index];
  }

  // Generate compliance report
  async generateComplianceReport(): Promise<any> {
    const totalRecords = this.processingRecords.length;
    const totalRequests = this.subjectRequests.length;
    const pendingRequests = this.subjectRequests.filter(r => r.status === 'pending').length;
    const totalBreaches = this.breachRecords.length;
    const containedBreaches = this.breachRecords.filter(b => b.status === 'contained' || b.status === 'resolved').length;

    return {
      summary: {
        totalProcessingRecords: totalRecords,
        totalSubjectRequests: totalRequests,
        pendingRequests: pendingRequests,
        totalBreaches: totalBreaches,
        containedBreaches: containedBreaches,
        complianceRate: totalRecords > 0 ? Math.round((containedBreaches / totalBreaches) * 100) : 100
      },
      processingRecords: this.processingRecords,
      recentRequests: this.subjectRequests.slice(-5),
      recentBreaches: this.breachRecords.slice(-5)
    };
  }

  // Handle data subject request
  async handleDataSubjectRequest(requestId: string, action: 'fulfill' | 'reject', response?: string): Promise<void> {
    const request = await this.getDataSubjectRequestById(requestId);
    if (!request) {
      throw new Error('Data subject request not found');
    }

    const status = action === 'fulfill' ? 'completed' : 'rejected';
    await this.updateDataSubjectRequestStatus(requestId, status, response);
  }

  // Report data breach to supervisor
  async reportBreachToSupervisor(breachId: string): Promise<void> {
    const breach = await this.getDataBreachRecordById(breachId);
    if (!breach) {
      throw new Error('Data breach record not found');
    }

    // In a real implementation, this would send a notification to the data protection supervisor
    console.log(`Reporting breach ${breachId} to supervisor`);

    await this.updateDataBreachRecord(breachId, {
      reportedToSupervisorAt: new Date().toISOString()
    });
  }

  // Report data breach to data subjects
  async reportBreachToDataSubjects(breachId: string): Promise<void> {
    const breach = await this.getDataBreachRecordById(breachId);
    if (!breach) {
      throw new Error('Data breach record not found');
    }

    // In a real implementation, this would send notifications to affected data subjects
    console.log(`Reporting breach ${breachId} to data subjects`);

    await this.updateDataBreachRecord(breachId, {
      reportedToDataSubjectsAt: new Date().toISOString()
    });
  }

  // Get compliance metrics
  getComplianceMetrics(): any {
    const thirtyDaysAgo = new Date();
    thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30);

    const recentRequests = this.subjectRequests.filter(
      r => new Date(r.createdAt) > thirtyDaysAgo
    );

    const recentBreaches = this.breachRecords.filter(
      b => new Date(b.discoveredAt) > thirtyDaysAgo
    );

    return {
      requests: {
        total: this.subjectRequests.length,
        recent: recentRequests.length,
        byType: this.subjectRequests.reduce((acc, request) => {
          acc[request.type] = (acc[request.type] || 0) + 1;
          return acc;
        }, {} as Record<string, number>),
        completionRate: this.subjectRequests.length > 0 
          ? Math.round(
              (this.subjectRequests.filter(r => r.status === 'completed').length / 
              this.subjectRequests.length) * 100
            )
          : 100
      },
      breaches: {
        total: this.breachRecords.length,
        recent: recentBreaches.length,
        contained: this.breachRecords.filter(b => b.status === 'contained' || b.status === 'resolved').length
      }
    };
  }
}

// Create singleton instance
const gdprComplianceManager = GDPRComplianceManager.getInstance();

export { gdprComplianceManager };
export type { DataProcessingRecord, DataSubjectRequest, DataBreachRecord };