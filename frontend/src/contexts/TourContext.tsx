import { createContext, useContext, useState, useEffect, useCallback, type ReactNode } from 'react';
import { driver, type DriveStep, type Driver } from 'driver.js';
import 'driver.js/dist/driver.css';
import { TOURS, type TourConfig, createDescriptionWithImage } from '../config/tours';
import { api } from '../lib/api';

interface TourContextType {
  // Tour state
  isTourActive: boolean;
  currentTourId: string | null;

  // Tour controls
  startTour: (tourId: string) => void;
  endTour: () => void;

  // Tour completion tracking
  completedTours: string[];
  hasCompletedTour: (tourId: string) => boolean;
  shouldShowTour: () => boolean;
  markTourSeen: () => void;
}

const TourContext = createContext<TourContextType | undefined>(undefined);

const STORAGE_KEY = 'jobezie_completed_tours';
const TOUR_SEEN_KEY = 'jobezie_tour_seen';

export function TourProvider({ children }: { children: ReactNode }) {
  const [isTourActive, setIsTourActive] = useState(false);
  const [currentTourId, setCurrentTourId] = useState<string | null>(null);
  const [completedTours, setCompletedTours] = useState<string[]>([]);
  const [driverInstance, setDriverInstance] = useState<Driver | null>(null);

  // Load completed tours from localStorage on mount
  useEffect(() => {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setCompletedTours(JSON.parse(stored));
      } catch {
        // Invalid JSON, reset
        localStorage.removeItem(STORAGE_KEY);
      }
    }

    // Also try to fetch from backend
    fetchTourStatus();
  }, []);

  // Fetch tour status from backend
  const fetchTourStatus = async () => {
    try {
      const response = await api.get('/auth/tour/status');
      const backendTours = response.data.completed_tours || [];

      // Merge with localStorage (union of both)
      const stored = localStorage.getItem(STORAGE_KEY);
      const localTours = stored ? JSON.parse(stored) : [];
      const merged = [...new Set([...localTours, ...backendTours])];

      setCompletedTours(merged);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(merged));
    } catch {
      // Backend endpoint may not exist yet, use localStorage only
    }
  };

  // Sync tour completion to backend
  const syncToBackend = async (tourId: string) => {
    try {
      await api.post('/auth/tour/complete', { tour_id: tourId });
    } catch {
      // Backend endpoint may not exist yet, localStorage is the fallback
    }
  };

  const hasCompletedTour = useCallback((tourId: string) => {
    return completedTours.includes(tourId);
  }, [completedTours]);

  const shouldShowTour = useCallback(() => {
    // Check if the main tour has been seen/dismissed
    const tourSeen = localStorage.getItem(TOUR_SEEN_KEY);
    return !tourSeen;
  }, []);

  const markTourSeen = useCallback(() => {
    localStorage.setItem(TOUR_SEEN_KEY, 'true');
  }, []);

  const markTourComplete = useCallback((tourId: string) => {
    setCompletedTours((prev) => {
      if (prev.includes(tourId)) return prev;
      const updated = [...prev, tourId];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
      return updated;
    });

    // Also mark as seen
    markTourSeen();

    // Sync to backend
    syncToBackend(tourId);
  }, [markTourSeen]);

  const startTour = useCallback((tourId: string) => {
    const tourConfig = TOURS[tourId];
    if (!tourConfig) {
      console.warn(`Tour "${tourId}" not found`);
      return;
    }

    // Convert our tour config to driver.js steps
    const driverSteps: DriveStep[] = tourConfig.steps.map((step) => ({
      element: step.element,
      popover: {
        title: step.title,
        description: createDescriptionWithImage(step.description, step.image),
        side: step.position || 'bottom',
        align: 'center',
      },
    }));

    // Create and configure driver instance
    const driverObj = driver({
      showProgress: true,
      steps: driverSteps,
      animate: true,
      allowClose: true,
      overlayClickNext: false,
      overlayColor: 'rgba(0, 0, 0, 0.5)',
      stagePadding: 8,
      stageRadius: 8,
      popoverClass: 'jobezie-tour-popover',
      nextBtnText: 'Next →',
      prevBtnText: '← Back',
      doneBtnText: 'Finish ✓',
      progressText: '{{current}} of {{total}}',
      onCloseClick: () => {
        // User clicked the X button to close
        markTourComplete(tourId);
        driverObj.destroy();
        setIsTourActive(false);
        setCurrentTourId(null);
        setDriverInstance(null);
      },
      onNextClick: () => {
        // Check if this is the last step (Finish button clicked)
        if (!driverObj.hasNextStep()) {
          // This is the last step - Finish button was clicked
          markTourComplete(tourId);
          driverObj.destroy();
          setIsTourActive(false);
          setCurrentTourId(null);
          setDriverInstance(null);
        } else {
          // Move to next step
          driverObj.moveNext();
        }
      },
      onDestroyStarted: () => {
        // Tour is being destroyed
        markTourComplete(tourId);
      },
      onDestroyed: () => {
        setIsTourActive(false);
        setCurrentTourId(null);
        setDriverInstance(null);
      },
    });

    setDriverInstance(driverObj);
    setCurrentTourId(tourId);
    setIsTourActive(true);

    // Start the tour after a brief delay to ensure DOM elements are ready
    setTimeout(() => {
      driverObj.drive();
    }, 100);
  }, [markTourComplete]);

  const endTour = useCallback(() => {
    if (driverInstance) {
      driverInstance.destroy();
    }
    setIsTourActive(false);
    setCurrentTourId(null);
    setDriverInstance(null);
    markTourSeen();
  }, [driverInstance, markTourSeen]);

  return (
    <TourContext.Provider
      value={{
        isTourActive,
        currentTourId,
        startTour,
        endTour,
        completedTours,
        hasCompletedTour,
        shouldShowTour,
        markTourSeen,
      }}
    >
      {children}
    </TourContext.Provider>
  );
}

// eslint-disable-next-line react-refresh/only-export-components
export function useTour() {
  const context = useContext(TourContext);
  if (context === undefined) {
    throw new Error('useTour must be used within a TourProvider');
  }
  return context;
}
