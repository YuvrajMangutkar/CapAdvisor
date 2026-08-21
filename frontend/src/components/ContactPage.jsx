import { useState } from 'react';
import { ArrowLeft, Mail, Send } from 'lucide-react';
import { sendContact } from '../api';

const SUPPORT_EMAIL = 'yuvrajmangutkar70@gmail.com';

export default function ContactPage({ onBack }) {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [status, setStatus] = useState({ loading: false, error: '', success: '' });

  function updateField(event) {
    setForm(current => ({ ...current, [event.target.name]: event.target.value }));
  }

  function handleSubmit(event) {
    event.preventDefault();
    setStatus({ loading: true, error: '', success: '' });
    sendContact(form)
      .then(result => setStatus({ loading: false, error: '', success: result.message }))
      .catch(error => setStatus({ loading: false, error: error.message, success: '' }));
  }

  return (
    <main className="contact-page relative z-10">
      <button type="button" className="back-button" onClick={onBack}>
        <ArrowLeft size={16} /> Back to advisor
      </button>

      <section className="contact-layout">
        <div className="contact-intro">
          <span className="kicker">Support desk</span>
          <h1>Let’s make your CAP list clearer.</h1>
          <p>Share the college, branch, category, and round details. Your message will be delivered directly to our support inbox.</p>
          <div className="contact-address"><Mail size={17} /> {SUPPORT_EMAIL}</div>
        </div>

        <form className="contact-form" onSubmit={handleSubmit}>
          <label htmlFor="contact-name">Your name</label>
          <input id="contact-name" name="name" value={form.name} onChange={updateField} required placeholder="Yuvraj Mangutkar" />

          <label htmlFor="contact-email">Email address</label>
          <input id="contact-email" name="email" type="email" value={form.email} onChange={updateField} required placeholder="you@example.com" />

          <label htmlFor="contact-subject">Subject</label>
          <input id="contact-subject" name="subject" value={form.subject} onChange={updateField} required placeholder="Question about my cutoff prediction" />

          <label htmlFor="contact-message">Message</label>
          <textarea id="contact-message" name="message" value={form.message} onChange={updateField} required rows="6" placeholder="Tell us what you need help with..." />

          <button type="submit" className="submit-button" disabled={status.loading}>
            <Send size={16} /> {status.loading ? 'Sending message...' : 'Send message'}
          </button>
          {status.error && <p className="contact-error" role="alert">{status.error}</p>}
          {status.success && <p className="contact-success" role="status">{status.success}</p>}
          <p className="contact-note">We will reply to the email address you provide.</p>
        </form>
      </section>
    </main>
  );
}
