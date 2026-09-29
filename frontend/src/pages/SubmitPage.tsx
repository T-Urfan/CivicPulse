import React, { useState } from 'react';
import { createComplaint } from '../api/client';
import type { ComplaintCreateRequest } from '../api/types';
import ApiErrorBanner from '../components/ApiErrorBanner';

const SubmitPage: React.FC = () => {
  const [text, setText] = useState('');
  const [location, setLocation] = useState('');
  const [contact, setContact] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    setSuccess(false);

    const payload: ComplaintCreateRequest = {
      text,
      location,
      ...(contact ? { reporter_contact: contact } : {}),
    };

    try {
      await createComplaint(payload);
      setSuccess(true);
      setText('');
      setLocation('');
      setContact('');
    } catch (err: any) {
      setError(err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="page-container submit-page" style={{ maxWidth: '680px', margin: '0 auto' }}>
      <div className="page-header" style={{ textAlign: 'center', marginBottom: '32px' }}>
        <h2>Submit a Complaint</h2>
        <p>Report municipal issues directly. Our integrated AI analyzes, classifies, and routes your request instantly.</p>
      </div>

      <ApiErrorBanner error={error} onDismiss={() => setError(null)} />

      {success && (
        <div 
          className="glass-panel" 
          style={{ 
            padding: '20px 24px', 
            marginBottom: '28px', 
            borderColor: 'rgba(48, 209, 88, 0.4)',
            background: 'rgba(48, 209, 88, 0.1)',
            display: 'flex',
            alignItems: 'center',
            gap: '16px',
            borderRadius: '20px'
          }}
        >
          <div style={{
            width: '36px',
            height: '36px',
            borderRadius: '50%',
            background: '#30D158',
            color: '#000',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            flexShrink: 0
          }}>
            ✓
          </div>
          <div>
            <h4 style={{ color: '#30D158', margin: '0 0 2px 0', fontSize: '1rem', fontWeight: 600 }}>Triage Completed</h4>
            <p style={{ margin: 0, fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
              Your complaint has been registered and scheduled for dispatch.
            </p>
          </div>
        </div>
      )}

      <form 
        onSubmit={handleSubmit} 
        className="glass-panel" 
        style={{ 
          padding: '36px', 
          display: 'flex', 
          flexDirection: 'column', 
          gap: '24px',
          borderRadius: '28px'
        }}
      >
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <label htmlFor="text">
              Complaint Description <span style={{ color: 'var(--apple-crimson)' }}>*</span>
            </label>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
              {text.length} chars
            </span>
          </div>
          <textarea
            id="text"
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Describe the issue in detail (e.g., Street lamp out on Elm St, water pressure drop, etc.)..."
            required
            style={{ resize: 'vertical', minHeight: '110px' }}
          />
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
            ✨ AI will automatically determine urgency and municipal department.
          </span>
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label htmlFor="location">
            Location <span style={{ color: 'var(--apple-crimson)' }}>*</span>
          </label>
          <input
            id="location"
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="E.g., North District, Sector 4, Main Boulevard"
            required
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label htmlFor="contact">
            Contact Information <span style={{ color: 'var(--text-tertiary)', fontWeight: 400 }}>(Optional)</span>
          </label>
          <input
            id="contact"
            type="text"
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            placeholder="Phone number, email, or citizen ID"
          />
        </div>

        <div style={{ paddingTop: '8px', display: 'flex', justifyContent: 'flex-end' }}>
          <button 
            type="submit" 
            disabled={isSubmitting || !text.trim() || !location.trim()} 
            style={{ 
              minWidth: '180px',
              padding: '13px 28px',
              fontSize: '0.95rem'
            }}
          >
            {isSubmitting ? (
              <>
                <span style={{ display: 'inline-block', animation: 'spin 1s linear infinite' }}>⟳</span>
                Submitting...
              </>
            ) : (
              'Submit Complaint'
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

export default SubmitPage;
