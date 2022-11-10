let select = document.querySelector(`select[name=kind]`);
let nameInput = document.querySelector(`input[name=full_name]`);
let emailInput = document.querySelector(`input[name=email]`);
let amountSpan = document.querySelector(`div[id=buy_ticket_amount]`);

let extraCheckboxes = Array.from(document.querySelectorAll(`input.extra`));

let alumDonationExtra = extraCheckboxes.filter((elt) =>
  elt.classList.contains("alum_donation")
);

alumDonationExtra.forEach((elt) =>
  elt.addEventListener("click", function () {
    recalculateAmount(select.options[select.selectedIndex]);
  })
);

let toToggle = [];

if (alumDonationExtra.length > 0) {
  toToggle.push(alumDonationExtra);
}

let alumJointExtra = extraCheckboxes.filter((elt) =>
  elt.classList.contains("alum_joint")
);

alumJointExtra.forEach((elt) =>
  elt.addEventListener("click", function () {
    recalculateAmount(select.options[select.selectedIndex]);
  })
);

if (alumJointExtra.length > 0) {
  toToggle.push(alumJointExtra);
}

select.addEventListener("change", function () {
  let selected = this.options[this.selectedIndex];
  if (toToggle.length > 0) {
    // toggle display of all extra checkboxes
    // and force refire of final calculation
    for (const checkboxes of toToggle) {
      let checkbox = checkboxes.find(
        (elt) => elt.dataset.kind == selected.value
      );
      checkboxes.forEach(
        (elt) => (elt.parentElement.parentElement.style.display = "none")
      );
      checkbox.parentElement.parentElement.style.display = "block";
      recalculateAmount(selected);
    }
  } else {
    // no checkbox change, just dropdown change
    recalculateAmount(selected);
  }
});

function recalculateAmount(selected) {
  let totalPrice = parseInt(selected.dataset.price);
  for (const checkboxes of toToggle) {
    // find checkboxes of that kind
    let checkbox = checkboxes.find((elt) => elt.dataset.kind == selected.value);
    if (checkbox.checked) {
      totalPrice += parseInt(checkbox.dataset.price);
    }
  }
  amountSpan.innerHTML = totalPrice;
}

// trigger caclulation
select.dispatchEvent(new Event("change"));
