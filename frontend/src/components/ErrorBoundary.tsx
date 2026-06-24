import { Component, type ReactNode } from 'react';

interface Props { children: ReactNode; }
interface State { hasError: boolean; error: Error | null; }

class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: any) {
    console.error('App Error:', error, info);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div style={{
          display: 'flex', flexDirection: 'column', alignItems: 'center',
          justifyContent: 'center', minHeight: '100vh',
          background: '#F8FAFC', color: '#1E293B',
          fontFamily: '-apple-system, sans-serif', padding: '2rem'
        }}>
          <h1 style={{ fontSize: '3rem', marginBottom: '0.5rem' }}>⚠️</h1>
          <h2 style={{ fontSize: '1.2rem', marginBottom: '1rem', color: '#EF4444' }}>
            Page Load Error
          </h2>
          <p style={{ color: '#64748B', marginBottom: '1rem' }}>
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => window.location.reload()}
            style={{
              padding: '8px 24px', borderRadius: '8px', border: 'none',
              background: '#3B82F6', color: '#fff', cursor: 'pointer',
              fontWeight: 600
            }}
          >
            Reload Page
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
