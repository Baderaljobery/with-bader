"use client";

import { Menu } from "lucide-react";
import { useState } from "react";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { Brand } from "./brand";
import { SidebarNav } from "./sidebar-nav";

export function MobileTopbar() {
  const [open, setOpen] = useState(false);

  return (
    <div className="flex items-center justify-between border-b border-[#E6EAF0] bg-white px-4 py-3 md:hidden">
      <Brand />
      <Sheet open={open} onOpenChange={setOpen}>
        <SheetTrigger
          render={<Button variant="outline" size="icon" aria-label="فتح قائمة التنقل" />}
        >
          <Menu className="size-5" />
        </SheetTrigger>
        <SheetContent side="right" className="w-72 px-4">
          <SheetHeader className="p-0">
            <SheetTitle className="sr-only">قائمة التنقل</SheetTitle>
            <Brand />
          </SheetHeader>
          <div className="mt-4">
            <SidebarNav onNavigate={() => setOpen(false)} />
          </div>
        </SheetContent>
      </Sheet>
    </div>
  );
}
