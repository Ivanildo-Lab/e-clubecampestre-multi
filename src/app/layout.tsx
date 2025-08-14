import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/toaster";
import { AuthProvider } from "@/hooks/auth-context";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Clube Manager - Sistema de Gestão de Clube Campestre",
  description: "Sistema completo para gestão de sócios, controle financeiro e administração de clubes campestres. Interface moderna e responsiva para web e mobile.",
  keywords: ["Clube Manager", "Gestão de Clubes", "Sócios", "Financeiro", "CRM", "Clube Campestre"],
  authors: [{ name: "Clube Manager Team" }],
  openGraph: {
    title: "Clube Manager - Sistema de Gestão de Clube Campestre",
    description: "Sistema completo para gestão de sócios e controle financeiro de clubes campestres",
    url: "https://clubemanager.com",
    siteName: "Clube Manager",
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "Clube Manager - Sistema de Gestão de Clube Campestre",
    description: "Sistema completo para gestão de sócios e controle financeiro de clubes campestres",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        <AuthProvider>
          {children}
          <Toaster />
        </AuthProvider>
      </body>
    </html>
  );
}
