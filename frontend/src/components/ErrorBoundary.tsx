import { Component, type ErrorInfo, type ReactNode } from 'react';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * Application-level React error boundary.
 * Required by the assignment to catch rendering errors gracefully.
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
  }

  render(): ReactNode {
    if (this.state.hasError) {
      return (
        <div className="error-boundary" role="alert">
          <h2>Something went wrong</h2>
          <p>
            An unexpected error occurred. Please try refreshing the page.
          </p>
          <details>
            <summary>Error Details</summary>
            <pre>{this.state.error?.message}</pre>
          </details>
          <button
            onClick={() => this.setState({ hasError: false, error: null })}
            className="error-boundary-retry"
          >
            Try Again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
