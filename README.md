Multi-Store Meat & Seafood E-Commerce (Blinkit-style, ZIP-based)
Goal:
Create a complete multi-store e-commerce platform for selling non-veg raw items (chicken, mutton, fish, prawns, kebabs, tikkas, etc.). The platform should work like Blinkit with fast, local delivery filtered by ZIP code, and an Admin → Multiple Stores → Customers model. Include store-owner independence, delivery agent workflow, real-time tracking, and a robust admin approval system for emergency closures.

Tech Stack (Python-first)
Backend: Python (Django preferred; Flask acceptable with equivalent structure)

Frontend: Server-rendered HTML, CSS, basic JavaScript (no JS frameworks)

Database: PostgreSQL (prod), SQLite (dev)

Auth: Django Auth or JWT where applicable; OTP via email/SMS (stub allowed)

Cache/Queues (optional but recommended): Redis for sessions/cart/ZIP lookup; simple task queue for notifications

Maps/Tracking: Google Maps (or OSRM) for live route & ETA

Hosting: AWS / Render / Railway / DigitalOcean

Env/Config: .env for secrets, settings for dev/prod

Roles & Access
Admin (platform owner)

Store Owner / Store Staff (per store)

Delivery Agent (per store)

Customer (end user)

Each store must have a unique Store ID/Code and unique credentials; stores operate independently within admin-assigned ZIP coverage.

Key Features
1) Product Categories & Catalog
Default categories:

Chicken (whole, cuts, boneless, marinated)

Mutton (bone-in, boneless, mince)

Fish (freshwater, seawater, fillets)

Prawns (small, medium, jumbo)

Marinated (kebab, tikka, seekh)

Admin can create new categories anytime; new categories/products auto-appear to users (subject to ZIP/store inventory).

Stores can add their own products and prices within allowed categories (optional admin approval).

Ingredients & Add-ons: Admin/Store can add ingredients (spices, marinades, herbs, oil) and link them to products for “Buy Together / Complete the Dish”.

Smart Suggestions: “Customers also bought” (simple rule-based initially; extendable).

2) ZIP & Store Coverage
On landing, user enters ZIP code → show available stores & only products deliverable to that ZIP.

Multi-ZIP per store with configurable: delivery fee, SLA/ETA, min order value.

Coverage can be via ZIP list or future map polygon.

Multi-cart: user can maintain separate carts for different stores serving the same ZIP.

3) Store Independence & Hours
Unique store auth + Store ID/Code.

Store-specific inventory, pricing, delivery slots, delivery agents, branding (logo, contact).

Working hours per store with auto-close outside hours.

Emergency Closure (Approval Flow): store can request temporary closure with reason & reopen time → visible only after admin approves. Admin can force-close/reopen stores.

4) Cart, Checkout, Payments
Basic JS cart (add/update/remove qty).

Totals: subtotal + delivery fee + tax (stub) + discounts.

Min order check per store/ZIP.

Checkout: address (pre-filled from ZIP), slot selection (30–90 min windows), express delivery option (paid).

Payments: UPI, cards, COD (mock gateway OK). Success/failure pages & order confirmation email.

5) Orders & Delivery
Order status: Placed → Accepted → Packed → Out for Delivery → Delivered/Cancelled.

Delivery Agents: per store; auto-assign based on load or proximity; manual override by store.

Tracking: customer sees live driver location and ETA; agent sees route hints.

Proof of Delivery: agent can upload photo/OTP at doorstep.

6) Admin Panel
Manage stores (create/edit/disable), approve closure requests, manage coverage ZIPs.

Global catalog control (approve store-added categories/products if moderation is on).

Commission & payout dashboard; export statements.

Reports: orders/day, revenue, AOV, top items, store performance.

Compliance/Quality: store rating (delivery time, cancellations, complaints). Auto warnings/suspension rules (admin override).

Help Support Oversight: admin can view all customer-store chats and take over any chat when necessary.

7) Store Owner Panel
Manage products, prices, images, ingredients & add-ons; bulk import via CSV.

Inventory per ZIP; low-stock alerts; option to auto-hide OOS items.

Manage delivery slots & delivery agents.

View orders; update statuses; assign agents; see delivery addresses on map.

Request emergency closure with reason + ETA (pending admin approval).

Customer Help Support: manage all customer queries/chats related to their store orders; respond in real-time.

8) Customer Experience
Login/register (email/phone, OTP), guest checkout allowed (optional).

Browse by category; filters: cut type, weight, freshness, price, in-stock.

“Frequently Bought Together” / “Complete the Dish”.

Choose preferred store if multiple serve the ZIP.

Real-time order tracking + push/email/SMS updates.

Loyalty & Rewards: earn/redeem points; referral bonus.

Customer Help Support: customers can initiate chat regarding products or orders; chats routed to store owner; admin can monitor and intervene.

9) Communication & Disputes
In-app chat: customer ↔ store/agent (visible to admin for audit & takeover).

Dispute management: flag orders; resolution workflow & notes.

Data Model (guidance, adapt as needed)
User/Customer

Store(id/code, name, auth users, hours, branding, status)

ZipArea(zip, city/state, active, fee, min_order, sla_minutes)

StoreZipCoverage(store↔zip, overrides)

Category

Product(global base fields)

StoreProduct(store↔product, price, availability, stock)

Ingredient & ProductIngredient(product↔ingredient, qty/use)

Suggestion(product↔add-ons/related)

DeliverySlot(store/zip, start/end, capacity)

Cart / CartItem(store-scoped)

Order, OrderItem

DeliveryAgent(store-scoped), Assignment

DeliveryTracking(lat/lng, timestamps, POD)

StoreClosureRequest(store, reason, requested_until, status)

ChatSession (customer, store, messages, status)

ChatMessage (sender, content, timestamp)

Rating/Review, Complaint/Dispute

LoyaltyLedger, Coupon (optional)

Payout/Commission (optional)

Views / URLs (minimum)
/ ZIP capture (persist in session)

/stores/ stores serving ZIP

/catalog/ & /p/<slug>/ product listing/detail (filtered by store/ZIP)

/cart/ (per store)

/checkout/ (address, slot, payment)

/order/<id>/ status & tracking

/auth/ login/register/OTP

/store/dashboard/ (owner panel)

/admin/closure-requests/ approvals

/chat/ customer support chat

/zip/change/ & /waitlist/ (for unsupported ZIPs)

UI/UX
Clean, appetizing visuals; mobile-first; accessible forms.

Sticky cart on mobile; clear CTAs.

Visible Open/Closed/Pending Approval status per store.

Prominent “Buy Together / Complete the Dish”.

Chat widget accessible from product & order pages for customers.

Store owners have dashboard chat panel; admin has master chat view with takeover option.

Notifications
Email/SMS for order events; push (optional).

Alerts: low stock, agent assignment, closure approval.

Chat notifications (new message alerts) for customers, stores, and admin.

Performance, Security, Reliability
Use caching for ZIP lookups, store availability, menus.

CSRF protection, rate limit OTP endpoints, password policies.

Logging & audit trails for admin actions (especially closures & chat takeovers).

Basic tests:

ZIP filtering & multi-store carts

Inventory decrement on order

Min order & fee per ZIP

Closure request requires admin approval to affect visibility

Tracking updates flow through to customer

Chat message flow and admin takeover

Seed Data & Deliverables
Seed: categories, a few products, 3–5 stores, multi-ZIP coverage, slots, agents.

Deliverables:

Full Django (or Flask) project with apps: accounts, stores, catalog, orders, delivery, locations, chat, core

Migrations + seed script/fixtures

HTML templates + CSS + minimal JS

Admin & Store dashboards wired

README with setup & run instructions

Postman collection (optional) for cart/checkout APIs
