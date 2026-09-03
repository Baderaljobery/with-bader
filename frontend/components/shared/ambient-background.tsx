/**
 * The app's atmosphere layer (design-notes.md, "Atmosphere system") - large,
 * heavily blurred, low-opacity radial glows in the brand teal/blue pair,
 * fixed behind the content area. Mounted once in AppShell so every page
 * gets it for free; never re-implement per page.
 *
 * Purely decorative (aria-hidden, pointer-events-none, negative z-index) -
 * never competes with content, never renders text or interactive elements.
 */
export function AmbientBackground() {
  return (
    <div aria-hidden="true" className="pointer-events-none fixed inset-0 -z-10 overflow-hidden">
      <div
        className="absolute -top-32 end-[-10%] size-[36rem] rounded-full opacity-70 blur-3xl"
        style={{ backgroundImage: "var(--glow-teal)" }}
      />
      <div
        className="absolute top-[28rem] start-[-14%] size-[40rem] rounded-full opacity-60 blur-3xl"
        style={{ backgroundImage: "var(--glow-blue)" }}
      />
      <div
        className="absolute bottom-[-10%] end-[18%] size-[28rem] rounded-full opacity-40 blur-3xl"
        style={{ backgroundImage: "var(--glow-teal)" }}
      />
    </div>
  );
}
