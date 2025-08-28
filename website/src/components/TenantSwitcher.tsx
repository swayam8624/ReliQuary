// Tenant Switcher Component
// Allows users to switch between multiple tenant organizations

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/lib/auth';
import { 
  BuildingOfficeIcon,
  ChevronDownIcon,
  PlusIcon,
  UserCircleIcon
} from '@heroicons/react/24/outline';

interface Tenant {
  id: string;
  name: string;
  tier: 'free' | 'starter' | 'professional' | 'enterprise';
  avatar?: string;
}

export default function TenantSwitcher() {
  const { authState, switchTenant } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isSwitching, setIsSwitching] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Mock data for demonstration
  // In a real implementation, this would come from the auth context or API
  const tenants: Tenant[] = [
    {
      id: 'tenant-1',
      name: 'Acme Corporation',
      tier: 'enterprise'
    },
    {
      id: 'tenant-2',
      name: 'Personal Projects',
      tier: 'free'
    },
    {
      id: 'tenant-3',
      name: 'Startup Ventures',
      tier: 'professional'
    }
  ];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleSwitchTenant = async (tenantId: string) => {
    setIsSwitching(true);
    try {
      await switchTenant(tenantId);
      setIsOpen(false);
    } catch (error) {
      console.error('Failed to switch tenant:', error);
    } finally {
      setIsSwitching(false);
    }
  };

  const getCurrentTenant = () => {
    return tenants.find(tenant => tenant.id === authState.tenant?.id) || tenants[0];
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'enterprise': return 'bg-purple-100 text-purple-800';
      case 'professional': return 'bg-blue-100 text-blue-800';
      case 'starter': return 'bg-green-100 text-green-800';
      case 'free': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-3 w-full p-2 rounded-lg hover:bg-gray-100 transition-colors"
        aria-haspopup="true"
        aria-expanded={isOpen}
      >
        <div className="flex-shrink-0">
          {authState.tenant?.avatar ? (
            <img 
              src={authState.tenant.avatar} 
              alt={authState.tenant.name} 
              className="h-8 w-8 rounded-full"
            />
          ) : (
            <div className="h-8 w-8 bg-primary-100 rounded-full flex items-center justify-center">
              <BuildingOfficeIcon className="h-5 w-5 text-primary-600" />
            </div>
          )}
        </div>
        
        <div className="flex-1 min-w-0 text-left">
          <p className="text-sm font-medium text-gray-900 truncate">
            {getCurrentTenant()?.name}
          </p>
          <p className="text-xs text-gray-500 truncate">
            {authState.user?.email}
          </p>
        </div>
        
        <ChevronDownIcon className={`h-5 w-5 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-72 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
          <div className="p-4 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-900">Switch Organization</h3>
          </div>
          
          <div className="max-h-60 overflow-y-auto">
            {tenants.map((tenant) => (
              <button
                key={tenant.id}
                onClick={() => handleSwitchTenant(tenant.id)}
                disabled={isSwitching}
                className={`w-full flex items-center space-x-3 p-3 text-left hover:bg-gray-50 transition-colors ${
                  tenant.id === authState.tenant?.id ? 'bg-blue-50' : ''
                }`}
              >
                <div className="flex-shrink-0">
                  {tenant.avatar ? (
                    <img 
                      src={tenant.avatar} 
                      alt={tenant.name} 
                      className="h-8 w-8 rounded-full"
                    />
                  ) : (
                    <div className="h-8 w-8 bg-gray-100 rounded-full flex items-center justify-center">
                      <BuildingOfficeIcon className="h-4 w-4 text-gray-600" />
                    </div>
                  )}
                </div>
                
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {tenant.name}
                  </p>
                  <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${getTierColor(tenant.tier)}`}>
                    {tenant.tier.charAt(0).toUpperCase() + tenant.tier.slice(1)}
                  </span>
                </div>
                
                {tenant.id === authState.tenant?.id && (
                  <div className="flex-shrink-0">
                    <div className="h-2 w-2 bg-green-500 rounded-full"></div>
                  </div>
                )}
              </button>
            ))}
          </div>
          
          <div className="p-2 border-t border-gray-200">
            <button className="w-full flex items-center space-x-2 p-2 text-sm text-gray-700 hover:bg-gray-50 rounded-md">
              <PlusIcon className="h-4 w-4" />
              <span>Create New Organization</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}