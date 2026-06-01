import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useState } from "react";
import { useAnalysisStore } from "@/store/useAnalysisStore";
import { Layout } from "@/components/Layout";

const geist = Geist({ variable: "--font-geist-sans", subsets: ["latin"] });
const geistMono = Geist_Mono({ variable: "--font-geist-mono", subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Atlas — AI Repository Intelligence",
  description: "Understand any GitHub repository in minutes. AI-powered architecture analysis, graph visualization, and intelligent Q&A.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <Layout>{children}</Layout>;
}
