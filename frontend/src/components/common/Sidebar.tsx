"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { BookOpen, LayoutDashboard, Library, BrainCircuit, RefreshCw, Settings, LogOut } from "lucide-react";
import { useAuthStore } from "@/lib/store/authStore";

type SidebarProps = React.HTMLAttributes<HTMLDivElement>;

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();
  const { signOut } = useAuthStore();

  const routes = [
    {
      label: "Dashboard",
      icon: LayoutDashboard,
      href: "/dashboard",
      active: pathname === "/dashboard",
    },
    {
      label: "Subjects",
      icon: Library,
      href: "/subjects",
      active: pathname?.startsWith("/subjects"),
    },
    {
      label: "Study",
      icon: BrainCircuit,
      href: "/study",
      active: pathname?.startsWith("/study"),
    },
    {
      label: "Sync Status",
      icon: RefreshCw,
      href: "/sync",
      active: pathname === "/sync",
    },
    {
        label: "Settings",
        icon: Settings,
        href: "/settings",
        active: pathname === "/settings",
      },
  ];

  return (
    <div className={cn("pb-12 h-full border-r bg-background", className)}>
      <div className="h-16 flex items-center px-6 border-b md:flex hidden">
        <Link href="/" className="flex items-center gap-2 font-bold text-xl text-primary">
            <BookOpen className="h-6 w-6" />
            <span>SmartStudy AI</span>
        </Link>
      </div>

      <div className="space-y-4 py-4 h-full flex flex-col">
        <div className="px-3 py-2 flex-1">
          <div className="space-y-1">
            {routes.map((route) => (
              <Button
                key={route.href}
                variant={route.active ? "secondary" : "ghost"}
                className={cn(
                  "w-full justify-start",
                  route.active && "bg-secondary"
                )}
                asChild
              >
                <Link href={route.href}>
                  <route.icon className="mr-2 h-4 w-4" />
                  {route.label}
                </Link>
              </Button>
            ))}
          </div>
        </div>
        
        {/* Bottom Section */}
        <div className="px-3 py-2 border-t">
            <div className="space-y-1">
                 <Button variant="ghost" className="w-full justify-start text-muted-foreground" onClick={() => signOut()}>
                     <LogOut className="mr-2 h-4 w-4" />
                     Logout
                 </Button>
            </div>
        </div>
      </div>
    </div>
  );
}
