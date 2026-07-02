# Estimate 1 - Screen Mockups

UI screen mockups for the contract note template management system. Created using Excalidraw MCP.

## Screenshots

| Screen | File |
|--------|------|
| Template List | [01-template-list.png](mockups/01-template-list.png) |
| Template Edit | [02-template-edit.png](mockups/02-template-edit.png) |
| Rules Configuration | [03-rules-config.png](mockups/03-rules-config.png) |
| Section Editor Modal | [04-section-editor.png](mockups/04-section-editor.png) |
| Shared Sections Library | [05-shared-sections.png](mockups/05-shared-sections.png) |

## Screen 1: Template List

The main entry point. An ordered table of all configured templates.

**Layout:**
- Page header: "Contract Note Template Management"
- Action button: [+ Create Template]
- Table columns: Priority (#), Template Name, Sections Count, Actions (Rules, Edit, Delete, Reorder handle)

**Key interactions:**
- Drag handle (↕️) to reorder priority
- ⚙️ Rules button opens the specification tree editor
- ✏️ Edit navigates to the template edit screen
- 🗑️ Delete prompts confirmation

---

## Screen 2: Template Edit

Editing a template's metadata and composing its sections.

**Layout:**
- Left panel: Template Details (Name, Description, Save Changes button)
- Centre panel: Sections list (ordered, drag to reorder)
  - Each row: #, Section Name, "(shared)" badge if applicable, Edit in Designer button, Remove button
- Right panel: Add Section controls ([+ New Section], [+ Add Shared Section])

**Key interactions:**
- Drag to reorder sections
- "Edit in Designer" opens the pdf-me Section Editor Modal
- "Add Shared Section" opens a picker from the Shared Sections Library
- Shared sections show a badge indicating they're shared
- T&Cs sections automatically positioned at the end

---

## Screen 3: Rules Configuration

Configuring the specification pattern (selection rule) for a template.

**Layout:**
- Left area: Specification Tree visualisation
  - Tree nodes: AND, OR, NOT (logical operators)
  - Leaf nodes: comparison expressions (e.g., "EQUALS: producttype = 'Fixed'")
  - Visual connecting lines between nodes
- Centre area: Tree Controls ([+ Add Logical Operator], [+ Add Comparison], [Delete Selected Node])
- Right area: Edit Node panel (Field dropdown, Operator dropdown, Value input)
- Bottom: [Save Rule] and [Cancel] buttons

**Key interactions:**
- Click a node to select it and populate the Edit Node panel
- Add operators/comparisons as children of selected node
- Delete removes selected node and its children
- Validation on save (all leaf nodes must have field + operator + value)

---

## Screen 4: Section Editor Modal

The pdf-me visual designer embedded in a modal for editing section layouts.

**Layout:**
- Left toolbar: Schema type tools ([T Text], [{} Multi-Variable], [⊞ Table], [↩ Undo], [↪ Redo])
- Centre canvas: Design area showing base PDF background with positioned, draggable fields
  - Fields shown as labelled rectangles (e.g., [customerName], [propertyTable])
- Right panel: Field Properties (Name, X, Y, Width, Height, Font Size, Alignment)
- Bottom: [Save Section] and [Cancel] buttons

**Key interactions:**
- Drag fields on canvas to reposition
- Click field to select and show properties
- Add new fields from toolbar
- Properties panel updates in real-time as fields are dragged
- Base PDF provides visual context for positioning

---

## Screen 5: Shared Sections Library

Managing reusable sections (headers, footers, T&Cs).

**Layout:**
- Header: "Shared Sections" with [+ Create Shared Section] button
- Centre: List of shared sections, each showing:
  - Section name
  - "Used by: X templates" count
  - Edit and Delete action buttons
- Right detail panel (on selection):
  - Name
  - Type (e.g., "Terms and Conditions")
  - "Used by" list showing template names
  - [Edit in Designer] button

**Key interactions:**
- Selecting a shared section shows the detail panel
- "Edit in Designer" opens the same pdf-me modal
- Delete shows warning if section is referenced by templates
- Creating a shared section prompts for name and type
