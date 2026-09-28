import React from 'react';
import { ApiError } from '../api/client';
import { ValidationErrorResponse } from '../api/types';

interface ApiErrorBannerProps {
  error: Error | ApiError | null;
  onDismiss?: () => void;
}

const ApiErrorBanner: React.FC<ApiErrorBannerProps> = ({ error, onDismiss }) => {
  if (!error) return null;

  let title = 'An unexpected error occurred';
  let messages: string[] = [error.message];

  if (error instanceof ApiError) {
    if (error.status === 400 && error.body && 'errors' in error.body) {
      const validationBody = error.body as ValidationErrorResponse;
      title = 'Validation Error';
      messages = validationBody.errors.map((err) => `${err.field}: ${err.message}`);
    } else if (error.status === 429) {
      title = 'Rate Limit Exceeded';
      const waitTime = error.retryAfter ? `${error.retryAfter} seconds` : 'a few moments';
      messages = [`You are submitting too fast. Please wait ${waitTime} before trying again.`];
    } else if (error.status === 409) {
      title = 'Conflict';
      messages = [error.body?.detail as string || 'Invalid state transition requested.'];
    } else {
      title = `Error ${error.status}`;
      messages = [error.body?.detail as string || error.statusText];
    }
  }

  return (
    <div className="api-error-banner" role="alert">
      <div className="api-error-content">
        <h4 className="api-error-title">{title}</h4>
        <ul className="api-error-list">
          {messages.map((msg, i) => (
            <li key={i}>{msg}</li>
          ))}
        </ul>
      </div>
      {onDismiss && (
        <button className="api-error-close" onClick={onDismiss} aria-label="Dismiss">
          &times;
        </button>
      )}
    </div>
  );
};

export default ApiErrorBanner;
