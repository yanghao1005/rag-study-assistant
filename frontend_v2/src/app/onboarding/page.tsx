import { Suspense } from "react";

import { OnboardingForm } from "@/components/auth/onboarding-form";

export default function OnboardingPage() {
  return (
    <Suspense fallback={<div className="px-6 py-8 text-sm text-muted-foreground">Loading onboarding...</div>}>
      <OnboardingForm />
    </Suspense>
  );
}

