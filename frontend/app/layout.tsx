import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "UniCompass | 德國選校陪跑",
  description: "循序整理背景、看懂推薦理由，再找到適合的德國學校。",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
  },
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="zh-Hant"><body>{children}</body></html>;
}
