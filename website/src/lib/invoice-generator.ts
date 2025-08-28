// Invoice Generation Service
// Automated billing system for generating and managing invoices

import { Invoice } from '@/lib/stripe';

interface InvoiceItem {
  description: string;
  quantity: number;
  unitPrice: number;
  amount: number;
}

interface InvoiceData {
  invoiceNumber: string;
  issueDate: string;
  dueDate: string;
  customer: {
    name: string;
    email: string;
    address: string;
  };
  company: {
    name: string;
    address: string;
    email: string;
    phone: string;
  };
  items: InvoiceItem[];
  subtotal: number;
  taxRate: number;
  taxAmount: number;
  total: number;
  currency: string;
  paymentStatus: 'paid' | 'pending' | 'overdue';
  notes?: string;
}

class InvoiceGenerator {
  private static instance: InvoiceGenerator;
  private invoiceCounter: number = 1000;
  private taxRate: number = 0.08; // 8% tax rate

  private constructor() {}

  // Singleton pattern
  public static getInstance(): InvoiceGenerator {
    if (!InvoiceGenerator.instance) {
      InvoiceGenerator.instance = new InvoiceGenerator();
    }
    return InvoiceGenerator.instance;
  }

  // Generate a new invoice number
  private generateInvoiceNumber(): string {
    const date = new Date();
    const year = date.getFullYear().toString().substr(2);
    const month = (date.getMonth() + 1).toString().padStart(2, '0');
    const counter = this.invoiceCounter++;
    return `INV-${year}${month}-${counter.toString().padStart(4, '0')}`;
  }

  // Format currency
  private formatCurrency(amount: number, currency: string = 'USD'): string {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency
    }).format(amount);
  }

  // Calculate tax amount
  private calculateTax(amount: number): number {
    return parseFloat((amount * this.taxRate).toFixed(2));
  }

  // Generate invoice from Stripe invoice data
  async generateInvoiceFromStripe(stripeInvoice: Invoice, customerData: any): Promise<InvoiceData> {
    // In a real implementation, this would convert Stripe invoice data to our format
    // For demo purposes, we'll create a mock invoice
    
    const items: InvoiceItem[] = [
      {
        description: 'ReliQuary Starter Plan - January 2024',
        quantity: 1,
        unitPrice: 99.00,
        amount: 99.00
      }
    ];

    const subtotal = items.reduce((sum, item) => sum + item.amount, 0);
    const taxAmount = this.calculateTax(subtotal);
    const total = subtotal + taxAmount;

    return {
      invoiceNumber: this.generateInvoiceNumber(),
      issueDate: new Date().toISOString().split('T')[0],
      dueDate: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toISOString().split('T')[0], // 30 days from now
      customer: {
        name: customerData.name || 'Customer',
        email: customerData.email || '',
        address: customerData.address || 'N/A'
      },
      company: {
        name: 'ReliQuary Inc.',
        address: '123 Security Street, San Francisco, CA 94105',
        email: 'billing@reliquary.io',
        phone: '+1 (555) 123-4567'
      },
      items,
      subtotal,
      taxRate: this.taxRate,
      taxAmount,
      total,
      currency: 'USD',
      paymentStatus: stripeInvoice.status === 'paid' ? 'paid' : 'pending',
      notes: 'Thank you for your business!'
    };
  }

  // Generate invoice HTML
  generateInvoiceHTML(invoice: InvoiceData): string {
    return `
      <!DOCTYPE html>
      <html>
      <head>
        <meta charset="utf-8">
        <title>Invoice ${invoice.invoiceNumber}</title>
        <style>
          body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
          .header { display: flex; justify-content: space-between; margin-bottom: 30px; }
          .company-info { text-align: right; }
          .invoice-title { font-size: 24px; font-weight: bold; color: #333; }
          .invoice-details { margin-bottom: 30px; }
          .invoice-details table { width: 100%; border-collapse: collapse; }
          .invoice-details th, .invoice-details td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
          .invoice-details th { background-color: #f5f5f5; }
          .items-table { width: 100%; border-collapse: collapse; margin-bottom: 20px; }
          .items-table th, .items-table td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
          .items-table th { background-color: #f5f5f5; }
          .totals { margin-left: auto; width: 300px; }
          .totals table { width: 100%; border-collapse: collapse; }
          .totals td { padding: 5px; }
          .total-row { font-weight: bold; border-top: 2px solid #333; }
          .footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="invoice-title">INVOICE</div>
            <div>Invoice #: ${invoice.invoiceNumber}</div>
            <div>Issue Date: ${invoice.issueDate}</div>
            <div>Due Date: ${invoice.dueDate}</div>
          </div>
          <div class="company-info">
            <div><strong>${invoice.company.name}</strong></div>
            <div>${invoice.company.address}</div>
            <div>${invoice.company.email}</div>
            <div>${invoice.company.phone}</div>
          </div>
        </div>

        <div class="invoice-details">
          <table>
            <tr>
              <td><strong>Bill To:</strong></td>
              <td><strong>Ship To:</strong></td>
            </tr>
            <tr>
              <td>${invoice.customer.name}</td>
              <td>${invoice.customer.name}</td>
            </tr>
            <tr>
              <td>${invoice.customer.email}</td>
              <td>${invoice.customer.email}</td>
            </tr>
            <tr>
              <td>${invoice.customer.address}</td>
              <td>${invoice.customer.address}</td>
            </tr>
          </table>
        </div>

        <table class="items-table">
          <thead>
            <tr>
              <th>Description</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Amount</th>
            </tr>
          </thead>
          <tbody>
            ${invoice.items.map(item => `
              <tr>
                <td>${item.description}</td>
                <td>${item.quantity}</td>
                <td>${this.formatCurrency(item.unitPrice, invoice.currency)}</td>
                <td>${this.formatCurrency(item.amount, invoice.currency)}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>

        <div class="totals">
          <table>
            <tr>
              <td>Subtotal:</td>
              <td>${this.formatCurrency(invoice.subtotal, invoice.currency)}</td>
            </tr>
            <tr>
              <td>Tax (${invoice.taxRate * 100}%):</td>
              <td>${this.formatCurrency(invoice.taxAmount, invoice.currency)}</td>
            </tr>
            <tr class="total-row">
              <td>Total:</td>
              <td>${this.formatCurrency(invoice.total, invoice.currency)}</td>
            </tr>
          </table>
        </div>

        <div class="footer">
          <p><strong>Notes:</strong> ${invoice.notes || ''}</p>
          <p>Payment Status: <strong>${invoice.paymentStatus.charAt(0).toUpperCase() + invoice.paymentStatus.slice(1)}</strong></p>
        </div>
      </body>
      </html>
    `;
  }

  // Generate invoice PDF (in a real implementation, this would use a PDF library)
  async generateInvoicePDF(invoice: InvoiceData): Promise<Buffer> {
    // In a real implementation, you would use a library like pdfkit or puppeteer
    // to generate a PDF from the HTML or directly
    // For demo purposes, we'll return a mock buffer
    console.log('Generating PDF for invoice:', invoice.invoiceNumber);
    return Buffer.from('Mock PDF content');
  }

  // Send invoice via email
  async sendInvoiceEmail(invoice: InvoiceData, pdfBuffer: Buffer): Promise<void> {
    // In a real implementation, this would send the invoice via email
    // using a service like SendGrid or Nodemailer
    console.log(`Sending invoice ${invoice.invoiceNumber} to ${invoice.customer.email}`);
  }

  // Generate and send invoice
  async generateAndSendInvoice(stripeInvoice: Invoice, customerData: any): Promise<void> {
    try {
      // Generate invoice data
      const invoiceData = await this.generateInvoiceFromStripe(stripeInvoice, customerData);
      
      // Generate PDF
      const pdfBuffer = await this.generateInvoicePDF(invoiceData);
      
      // Send email
      await this.sendInvoiceEmail(invoiceData, pdfBuffer);
      
      console.log(`Invoice ${invoiceData.invoiceNumber} generated and sent successfully`);
    } catch (error) {
      console.error('Failed to generate and send invoice:', error);
      throw new Error('Failed to generate and send invoice');
    }
  }

  // Get invoice by number
  async getInvoiceByNumber(invoiceNumber: string): Promise<InvoiceData | null> {
    // In a real implementation, this would fetch the invoice from a database
    // For demo purposes, we'll return null
    return null;
  }

  // Get all invoices for a customer
  async getCustomerInvoices(customerEmail: string): Promise<InvoiceData[]> {
    // In a real implementation, this would fetch all invoices for a customer from a database
    // For demo purposes, we'll return an empty array
    return [];
  }

  // Update invoice payment status
  async updateInvoicePaymentStatus(invoiceNumber: string, status: 'paid' | 'pending' | 'overdue'): Promise<void> {
    // In a real implementation, this would update the invoice status in a database
    console.log(`Updating invoice ${invoiceNumber} status to ${status}`);
  }

  // Get overdue invoices
  async getOverdueInvoices(): Promise<InvoiceData[]> {
    // In a real implementation, this would fetch overdue invoices from a database
    // For demo purposes, we'll return an empty array
    return [];
  }

  // Send reminder for overdue invoices
  async sendOverdueReminders(): Promise<void> {
    try {
      const overdueInvoices = await this.getOverdueInvoices();
      
      for (const invoice of overdueInvoices) {
        // In a real implementation, this would send reminder emails
        console.log(`Sending reminder for overdue invoice ${invoice.invoiceNumber}`);
      }
      
      console.log(`Sent reminders for ${overdueInvoices.length} overdue invoices`);
    } catch (error) {
      console.error('Failed to send overdue reminders:', error);
      throw new Error('Failed to send overdue reminders');
    }
  }
}

// Create singleton instance
const invoiceGenerator = InvoiceGenerator.getInstance();

export { invoiceGenerator };
export type { InvoiceData, InvoiceItem };