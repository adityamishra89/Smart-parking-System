const slotGrid = document.getElementById("slotGrid");
const bookingModal = document.getElementById("bookingModal");
const closeModalBtn = document.getElementById("closeModal");
const bookingForm = document.getElementById("bookingForm");
const selectedSlotIdInput = document.getElementById("selectedSlotId");
const slotNumberText = document.getElementById("slotNumberText");
const messageBox = document.getElementById("messageBox");
const loader = document.getElementById("loader");
const validateBookingBtn = document.getElementById("validateBookingBtn");
const payBtn = document.getElementById("payBtn");

let slots = [];

function showLoader(isVisible) {
  loader.classList.toggle("hidden", !isVisible);
}

function showMessage(message, type = "success") {
  messageBox.textContent = message;
  messageBox.classList.remove("message-success", "message-error");
  messageBox.classList.add(type === "success" ? "message-success" : "message-error");
}

async function loadSlots() {
  slotGrid.innerHTML = "<p style='color:white;'>Loading slots...</p>";
  try {
    const response = await fetch("/slots");
    const result = await response.json();

    if (!result.success) {
      slotGrid.innerHTML = `<p style='color:white;'>${result.message}</p>`;
      return;
    }

    slots = result.slots;
    renderSlots();
  } catch (error) {
    slotGrid.innerHTML = "<p style='color:white;'>Unable to load slots. Check backend connection.</p>";
  }
}

function renderSlots() {
  if (!slots.length) {
    slotGrid.innerHTML = "<p style='color:white;'>No slots found.</p>";
    return;
  }

  slotGrid.innerHTML = "";

  slots.forEach((slot) => {
    const card = document.createElement("article");
    card.className = "slot-card";

    const isAvailable = slot.status === "Available";

    card.innerHTML = `
      <h3>Slot #${slot.id}</h3>
      <span class="status-pill ${isAvailable ? "status-available" : "status-booked"}">
        ${slot.status}
      </span>
      <button class="btn ${isAvailable ? "btn-primary" : "btn-booked"}" ${isAvailable ? "" : "disabled"}>
        ${isAvailable ? "Book Slot" : "Already Booked"}
      </button>
    `;

    const button = card.querySelector("button");
    if (isAvailable) {
      button.addEventListener("click", () => openBookingModal(slot.id));
    }

    slotGrid.appendChild(card);
  });
}

function resetModal() {
  bookingForm.reset();
  payBtn.disabled = true;
  validateBookingBtn.disabled = false;
  showMessage("");
}

function openBookingModal(slotId) {
  resetModal();
  selectedSlotIdInput.value = slotId;
  slotNumberText.textContent = `#${slotId}`;
  bookingModal.classList.remove("hidden");
}

function closeModal() {
  bookingModal.classList.add("hidden");
}

closeModalBtn.addEventListener("click", closeModal);
bookingModal.addEventListener("click", (event) => {
  if (event.target === bookingModal) closeModal();
});

// Step 1: validate booking request
bookingForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  showLoader(true);
  showMessage("");

  const payload = {
    name: document.getElementById("name").value.trim(),
    vehicle: document.getElementById("vehicle").value.trim(),
    slot_id: Number(selectedSlotIdInput.value),
  };

  try {
    const response = await fetch("/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok || !result.success) {
      showMessage(result.message || "Booking validation failed.", "error");
      return;
    }

    showMessage(result.message, "success");
    payBtn.disabled = false;
    validateBookingBtn.disabled = true;
  } catch (error) {
    showMessage("Server error during booking validation.", "error");
  } finally {
    showLoader(false);
  }
});

// Step 2: fake payment + final booking
payBtn.addEventListener("click", async () => {
  showLoader(true);
  showMessage("");

  const payload = {
    name: document.getElementById("name").value.trim(),
    vehicle: document.getElementById("vehicle").value.trim(),
    slot_id: Number(selectedSlotIdInput.value),
  };

  try {
    const response = await fetch("/payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const result = await response.json();

    if (!response.ok || !result.success) {
      showMessage(result.message || "Payment failed.", "error");
      return;
    }

    showMessage(result.message, "success");
    payBtn.disabled = true;

    await loadSlots();
    setTimeout(closeModal, 900);
  } catch (error) {
    showMessage("Server error during payment.", "error");
  } finally {
    showLoader(false);
  }
});

loadSlots();
