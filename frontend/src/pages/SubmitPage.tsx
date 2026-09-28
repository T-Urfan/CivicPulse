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
    <div className="page-container submit-page">
      <h2>Submit a Complaint</h2>
      <p className="text-muted">
        Report civic issues in your area. Our AI system will automatically categorize and prioritize your request.
      </p>

      <ApiErrorBanner error={error} onDismiss={() => setError(null)} />

      {success && (
        <div className="glass-panel" style={{ padding: '20px', marginBottom: '24px', borderColor: 'var(--success-color)' }}>
          <h4 style={{ color: 'var(--success-color)', margin: '0 0 8px 0' }}>Success</h4>
          <p style={{ margin: 0 }}>Your complaint has been submitted and triaged successfully.</p>
        </div>
      )}

      <form onSubmit={handleSubmit} className="glass-panel" style={{ padding: '30px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label htmlFor="text">Complaint Description <span style={{ color: 'var(--error-color)' }}>*</span></label>
          <textarea
            id="text"
            rows={4}
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="E.g., The street light is broken on main road..."
            required
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label htmlFor="location">Location <span style={{ color: 'var(--error-color)' }}>*</span></label>
          <input
            id="location"
            type="text"
            value={location}
            onChange={(e) => setLocation(e.target.value)}
            placeholder="E.g., Block 5, Clifton"
            required
          />
        </div>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          <label htmlFor="contact">Contact Information (Optional)</label>
          <input
            id="contact"
            type="text"
            value={contact}
            onChange={(e) => setContact(e.target.value)}
            placeholder="Phone number or email"
          />
        </div>

        <button type="submit" disabled={isSubmitting} style={{ alignSelf: 'flex-start', marginTop: '10px' }}>
          {isSubmitting ? 'Submitting...' : 'Submit Complaint'}
        </button>
      </form>
    </div>
  );
};

export default SubmitPage;
