import Link from "next/link";

export default function Navbar() {
  return (
    <nav className="border-b border-gray-800 bg-gray-900 px-6 py-4 flex items-center justify-between">
      <Link href="/" className="flex items-center space-x-2">
        <span className="text-2xl">🎬</span>
        <span className="text-xl font-bold bg-gradient-to-r from-purple-400 to-pink-500 bg-clip-text text-transparent">
          AI Video Clipper
        </span>
      </Link>
      <div className="flex items-center space-x-6 text-sm font-medium">
        <Link href="/" className="text-gray-300 hover:text-white transition">
          Projects
        </Link>
        <Link href="/settings" className="text-gray-300 hover:text-white transition">
          Settings ⚙️
        </Link>
      </div>
    </nav>
  );
}
