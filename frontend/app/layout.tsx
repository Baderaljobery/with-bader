import type { Metadata } from "next";

import { Toaster } from "@/components/ui/sonner";
import { thmanyahSans, thmanyahSerifDisplay, thmanyahSerifText } from "@/lib/fonts";
import { QueryProvider } from "@/providers/query-provider";
import "./globals.css";

export const metadata: Metadata = {
  title: "With Bader",
  description: "منصة متكاملة لإدارة الضيوف والمقابلات والمحتوى.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html
      lang="ar"
      dir="rtl"
      className={`${thmanyahSans.variable} ${thmanyahSerifDisplay.variable} ${thmanyahSerifText.variable} h-full antialiased`}
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
