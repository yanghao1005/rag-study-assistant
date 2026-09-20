import Link from "next/link";
import { BookOpen, LogOut, Menu } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useAuthStore } from "@/lib/store/authStore";
import { Sidebar } from "@/components/common/Sidebar";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Sheet, SheetContent, SheetTrigger } from "@/components/ui/sheet";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useRouter } from "next/navigation";
import { useSyncStore } from "@/lib/store/syncStore";

export function Navbar() {
  const { user, signOut } = useAuthStore();
  const { isOnline, isSyncing, queuedMutations } = useSyncStore();
  const router = useRouter();

  const handleSignOut = async () => {
    await signOut();
    router.push("/");
  };

  return (
    <nav className="border-b bg-background sticky top-0 z-30">
      <div className="w-full px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-4">
             {/* Mobile Sidebar Trigger */}
            <Sheet>
                <SheetTrigger asChild>
                    <Button variant="ghost" size="icon" className="md:hidden">
                        <Menu className="h-5 w-5" />
                    </Button>
                </SheetTrigger>
                <SheetContent side="left" className="p-0 w-72">
                    <div className="h-16 flex items-center px-6 border-b">
                        <Link href="/" className="flex items-center gap-2 font-bold text-xl text-primary">
                            <BookOpen className="h-6 w-6" />
                            <span>SmartStudy AI</span>
                        </Link>
                    </div>
                    <Sidebar />
                </SheetContent>
            </Sheet>

            <Link href="/" className="flex items-center gap-2 font-bold text-xl text-primary md:flex hidden">
            {/* Logo is in Sidebar for desktop */}
            </Link>
        </div>

        <div className="flex items-center gap-4">
          <span className="text-xs text-muted-foreground hidden sm:inline-block">
            {isOnline
              ? (isSyncing ? 'Syncing...' : queuedMutations > 0 ? `Online • ${queuedMutations} queued` : 'Online')
              : `Offline • ${queuedMutations} known pending`}
          </span>
          {user ? (
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="relative h-8 w-8 rounded-full">
                  <Avatar className="h-8 w-8">
                    <AvatarFallback>{user.email?.charAt(0).toUpperCase()}</AvatarFallback>
                  </Avatar>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="w-56" align="end" forceMount>
                <DropdownMenuLabel className="font-normal">
                  <div className="flex flex-col space-y-1">
                    <p className="text-sm font-medium leading-none">Account</p>
                    <p className="text-xs leading-none text-muted-foreground">
                      {user.email}
                    </p>
                  </div>
                </DropdownMenuLabel>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleSignOut}>
                  <LogOut className="mr-2 h-4 w-4" />
                  <span>Log out</span>
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          ) : (
            <>
              <Button variant="outline" size="sm" asChild>
                <Link href="/login">Sign In</Link>
              </Button>
              <Button size="sm" asChild>
                 <Link href="/login?tab=signup">Get Started</Link>
              </Button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
