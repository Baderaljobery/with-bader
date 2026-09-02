import type { Metadata } from "next";
import { Alexandria, Tajawal } from "next/font/google";

import { Toaster } from "@/components/ui/sonner";
import { QueryProvider } from "@/providers/query-provider";
import "./globals.css";

const tajawal = Tajawal({
  variable: "--font-sans",
  subsets: ["arabic", "latin"],
  weight: ["400", "500", "700"],
});

const alexandria = Alexandria({
  variable: "--font-heading",
  subsets: ["arabic", "latin"],
  weight: ["500", "600", "700"],
});

export const metadata: Metadata = {
  title: "With Bader",
  description: "منصة متكاملة لإدارة الضيوف والمقابلات والمحتوى.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="ar"
      dir="rtl"
      className={`${tajawal.variable} ${alexandria.variable} h-full antialiased`}
    >
      <body className="h-full">
        <QueryProvider>
          {children}
          <Toaster position="top-center" richColors />
        </QueryProvider>
      </body>
    </html>
  );
}
