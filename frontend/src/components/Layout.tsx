"use client";

import type { ReactNode } from "react";

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <html lang="en" className="dark">
      <body className={`font-sans antialiased`}>{children}</body>
    </html>
  );
}
