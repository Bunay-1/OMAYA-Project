import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

interface Props {
  children?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class GlobalErrorBoundary extends Component<Props, State> {
  public state: State = {
    hasError: false,
    error: null
  };

  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Uncaught error:', error, errorInfo);
  }

  public render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-[#0a0e1a] p-6">
          <div className="glass-panel max-w-md w-full p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-[#ff3366]/10 flex items-center justify-center mx-auto mb-6">
              <AlertCircle className="w-8 h-8 text-[#ff3366]" />
            </div>
            <h1 className="text-2xl font-display font-bold text-white mb-2">Something went wrong</h1>
            <p className="text-gray-400 mb-8">
              The application encountered an unexpected error. Our team has been notified.
            </p>
            <button
              onClick={() => window.location.reload()}
              className="w-full py-3 rounded-xl bg-gradient-to-r from-[#00ff88] to-[#00d9ff] text-[#0a0e1a] font-bold flex items-center justify-center gap-2 hover:opacity-90 transition-opacity"
            >
              <RefreshCw className="w-4 h-4" />
              Reload Application
            </button>
            {process.env.NODE_ENV === 'development' && (
              <div className="mt-6 p-4 bg-black/40 rounded-lg text-left overflow-auto max-h-40">
                <p className="text-xs font-mono text-[#ff3366]">{this.state.error?.toString()}</p>
              </div>
            )}
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
