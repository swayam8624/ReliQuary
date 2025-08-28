// Protected Route Component
// Handles authentication and authorization for different tenant tiers and user roles

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth';
import { 
  ExclamationTriangleIcon,
  ArrowPathIcon
} from '@heroicons/react/24/outline';

interface ProtectedRouteProps {
  children: React.ReactNode;
  requiredTier?: 'free' | 'starter' | 'professional' | 'enterprise';
  requiredPermission?: string;
  requireAdmin?: boolean;
}

export default function ProtectedRoute({
  children,
  requiredTier,
  requiredPermission,
  requireAdmin
}: ProtectedRouteProps) {
  const { authState, refreshAuth } = useAuth();
  const router = useRouter();
  const [isChecking, setIsChecking] = useState(true);
  const [accessDenied, setAccessDenied] = useState(false);

  useEffect(() => {
    const checkAccess = async () => {
      try {
        // If not authenticated, redirect to login
        if (!authState.isAuthenticated) {
          // Try to refresh auth state
          try {
            await refreshAuth();
          } catch (error) {
            // If refresh fails, redirect to login
            router.push('/login');
            return;
          }
        }

        // Check tier requirements
        if (requiredTier) {
          const tierOrder = ['free', 'starter', 'professional', 'enterprise'];
          const currentTierIndex = tierOrder.indexOf(authState.tenant?.tier || 'free');
          const requiredTierIndex = tierOrder.indexOf(requiredTier);
          
          if (currentTierIndex < requiredTierIndex) {
            setAccessDenied(true);
            return;
          }
        }

        // Check admin requirement
        if (requireAdmin && authState.user?.role !== 'admin') {
          setAccessDenied(true);
          return;
        }

        // Check permission requirement
        if (requiredPermission) {
          // In a real implementation, this would check against user permissions
          // For now, we'll assume all authenticated users have basic permissions
          // except for admin-only features
          if (requireAdmin && authState.user?.role !== 'admin') {
            setAccessDenied(true);
            return;
          }
        }

        // All checks passed
        setIsChecking(false);
      } catch (error) {
        console.error('Access check failed:', error);
        router.push('/login');
      }
    };

    checkAccess();
  }, [authState, requiredTier, requiredPermission, requireAdmin, router, refreshAuth]);

  // Show loading state
  if (isChecking) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking access permissions...</p>
        </div>
      </div>
    );
  }

  // Show access denied message
  if (accessDenied) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
          <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
            <ExclamationTriangleIcon className="h-6 w-6 text-red-600" />
          </div>
          <h3 className="mt-4 text-lg font-medium text-gray-900">Access Denied</h3>
          <div className="mt-2 text-sm text-gray-600">
            {requiredTier ? (
              <p>
                This feature requires a <span className="font-semibold">{requiredTier}</span> plan or higher. 
                Please upgrade your subscription to access this feature.
              </p>
            ) : requireAdmin ? (
              <p>
                This feature is only available to organization administrators.
              </p>
            ) : (
              <p>
                You don't have permission to access this resource.
              </p>
            )}
          </div>
          <div className="mt-6">
            <button
              onClick={() => router.push('/dashboard')}
              className="btn-primary"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Render children if all checks pass
  return <>{children}</>;
}

// Higher-order component for easier usage
export function withProtectedRoute(
  WrappedComponent: React.ComponentType<any>,
  protectionOptions: Omit<ProtectedRouteProps, 'children'> = {}
) {
  return function ProtectedComponent(props: any) {
    return (
      <ProtectedRoute {...protectionOptions}>
        <WrappedComponent {...props} />
      </ProtectedRoute>
    );
  };
}