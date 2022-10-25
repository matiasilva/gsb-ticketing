let select = document.querySelector(`select[name=kind]`);
let nameInput = document.querySelector(`input[name=full_name]`);
let emailInput = document.querySelector(`input[name=email]`);
let amountSpan = document.querySelector(`div[id=buy_ticket_amount]`);
let extraCheckboxes = Array.from(document.querySelectorAll(`input.extra`));
extraCheckboxes = extraCheckboxes.filter((elt) =>
  elt.classList.contains("alum_donation")
);
extraCheckboxes.forEach((elt) =>
  elt.addEventListener("click", function () {
    recalculateAmount(select.options[select.selectedIndex], this);
  })
);

select.addEventListener("change", function () {
  let selected = this.options[this.selectedIndex];
  if (extraCheckboxes.length > 0) {
    let checkbox = extraCheckboxes.find(
      (elt) => elt.dataset.kind == selected.value
    );
    extraCheckboxes.forEach(
      (elt) => (elt.parentElement.parentElement.style.display = "none")
    );
    checkbox.parentElement.parentElement.style.display = "block";
    recalculateAmount(selected, checkbox);
  } else {
    recalculateAmount(selected);
  }
});

function recalculateAmount(selected, checkbox) {
  let totalPrice = parseInt(selected.dataset.price);
  if (checkbox && checkbox.checked) {
    totalPrice += parseInt(checkbox.dataset.price);
  }
  amountSpan.innerHTML = totalPrice;
}

select.dispatchEvent(new Event("change"));
