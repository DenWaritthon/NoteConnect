"use client";

import { useRouter, usePathname } from "next/navigation";
import { useState } from "react";
import { Menu, X } from "lucide-react";
import Logo from "@/public/Logo.svg";

export default function Header() {
    const router = useRouter();
    const pathname = usePathname();
    const [open, setOpen] = useState(false);

    const linkStyle = (path: string) =>
        `cursor-pointer ${pathname === path
            ? "font-semibold underline"
            : "text-gray-500 hover:text-black"
        }`;

    const navigate = (path: string) => {
        setOpen(false);
        router.push(path);
    };

    return (
        <header className="fixed left-0 top-0 z-50 flex w-full items-center justify-between bg-white/80 px-4 py-3 shadow-sm backdrop-blur sm:px-8 sm:py-4">
            <div
                onClick={() => navigate("/")}
                className="flex cursor-pointer items-center gap-2"
            >
                <Logo className="h-10 w-10" />
            </div>

            <nav className="hidden gap-8 text-sm md:flex">
                <span onClick={() => navigate("/")} className={linkStyle("/")}>
                    HOME
                </span>
                <span
                    onClick={() => navigate("/notes")}
                    className={linkStyle("/notes")}
                >
                    NOTES
                </span>
            </nav>

            <button
                className="rounded-lg p-2 md:hidden"
                onClick={() => setOpen(!open)}
                aria-label={open ? "Close menu" : "Open menu"}
                aria-expanded={open}
            >
                {open ? <X size={22} /> : <Menu size={22} />}
            </button>

            {open && (
                <div className="absolute right-4 top-16 w-40 rounded-xl bg-white p-4 shadow-soft md:hidden">
                    <div onClick={() => navigate("/")} className="py-2 text-sm">
                        HOME
                    </div>
                    <div onClick={() => navigate("/notes")} className="py-2 text-sm">
                        NOTES
                    </div>
                </div>
            )}
        </header>
    );
}
