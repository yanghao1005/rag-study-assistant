"use client";

import type { ElementType, ReactNode } from "react";
import { createContext, use } from "react";

import { cn } from "@/lib/utils";

export const DeckActiveContext = createContext(0);
export const SlideOrderContext = createContext(0);

export function Slide({
  notes,
  variant,
  children,
}: {
  notes: string;
  variant?: "section";
  children: ReactNode;
}) {
  const active = use(DeckActiveContext);
  const order = use(SlideOrderContext);
  return (
    <section
      className={cn(
        "tfm-slide",
        variant === "section" && "is-section",
        active === order && "is-active",
      )}
    >
      <div className="tfm-frame">{children}</div>
      <aside className="tfm-notes">{notes}</aside>
    </section>
  );
}

export function Kicker({ children }: { children: ReactNode }) {
  return <p className="tfm-kicker">{children}</p>;
}

export function Title({
  as = "h2",
  children,
}: {
  as?: "h1" | "h2";
  children: ReactNode;
}) {
  const Tag = as;
  return <Tag>{children}</Tag>;
}

export function Lede({ children, className }: { children: ReactNode; className?: string }) {
  return <p className={cn("tfm-lede", className)}>{children}</p>;
}

export function Meta({ children }: { children: ReactNode }) {
  return <p className="tfm-meta">{children}</p>;
}

export function Stack({
  center = false,
  children,
}: {
  center?: boolean;
  children: ReactNode;
}) {
  return <ul className={cn("tfm-stack", center && "is-center")}>{children}</ul>;
}

export function Frag({
  as: Tag = "div",
  className,
  children,
}: {
  as?: ElementType;
  className?: string;
  children: ReactNode;
}) {
  return <Tag className={cn("tfm-fragment", className)}>{children}</Tag>;
}

export function Card({
  label,
  title,
  children,
}: {
  label: string;
  title: string;
  children: ReactNode;
}) {
  return (
    <article className="tfm-card tfm-fragment">
      <span>{label}</span>
      <strong>{title}</strong>
      <p>{children}</p>
    </article>
  );
}
