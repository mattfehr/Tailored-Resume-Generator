import "./globals.css";
import NavBar from "../components/NavBar";

export const metadata = {
  title: "ResuMatch AI",
  description: "AI-powered resume tailoring platform",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-white">
        <NavBar />
        <main>{children}</main>
      </body>
    </html>
  );
}
