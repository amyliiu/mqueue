"use client";
import { useState, FormEvent } from 'react';
import styles from './badminton-queue.module.css';

const API_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000';

function getOrdinalSuffix(position: number): string {
  const j = position % 10;
  const k = position % 100;
  if (j === 1 && k !== 11) {
    return 'st';
  }
  if (j === 2 && k !== 12) {
    return 'nd';
  }
  if (j === 3 && k !== 13) {
    return 'rd';
  }
  return 'th';
}

export default function BadmintonQueue() {
  const [isLoading, setIsLoading] = useState(false);
  const [showQueueStatus, setShowQueueStatus] = useState(false);
  const [queuePosition, setQueuePosition] = useState<number | null>(null);

  async function addToQueue(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setIsLoading(true);

    const form = event.currentTarget;
    const formData = new FormData(form);
    const name = formData.get('name') as string;
    const phoneNumber = formData.get('phoneNumber') as string;

    try {
      const response = await fetch(`${API_URL}/api/v1/queue`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, phoneNumber }),
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.detail || 'Failed to add to queue');
      }

      setQueuePosition(data.position);
      setShowQueueStatus(true);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className={styles.container}>
      {showQueueStatus ? (
        <div className={styles.queueStatus}>
          <h2>You are</h2>
          <div className={styles.positionDisplay}>
            {queuePosition}{getOrdinalSuffix(queuePosition!)}
          </div>
          <h2>in the Queue!</h2>
          
          <div className={styles.menuList}>
            <div className={styles.menuItem}>Menu item</div>
            <div className={styles.menuItem}>Menu item</div>
            <div className={styles.menuItem}>Menu item</div>
            <div className={styles.menuItem}>Menu item</div>
            <div className={`${styles.menuItem} ${styles.activeMenuItem}`}>Menu item</div>
          </div>
        </div>
      ) : (
        <>
          <h1 className={styles.title}>MQueue</h1>
          <form onSubmit={addToQueue} className={styles.queueForm}>
            <input
              type="text"
              name="name"
              className={styles.inputField}
              placeholder="Name *"
              required
            />
            <input
              type="tel"
              name="phoneNumber"
              className={styles.inputField}
              placeholder="Phone Number *"
              required
            />
            <div className={styles.checkboxContainer}>
              <input type="checkbox" id="consent" required />
              <label htmlFor="consent">
                By providing your information you opt in to receiving texts from our service. 
                Messaging rates may apply.
              </label>
            </div>
            <button
              type="submit"
              className={styles.submitButton}
              disabled={isLoading}
            >
              {isLoading ? 'Adding...' : 'Add to Queue'}
            </button>
          </form>
        </>
      )}
    </div>
  );
}