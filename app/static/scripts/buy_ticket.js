let checkbox = document.querySelector(`input[name=is_own]`);
let select = document.querySelector(`select[name=kind]`);
let nameInput = document.querySelector(`input[name=full_name]`);
let emailInput = document.querySelector(`input[name=email]`);
let amountInput = document.querySelector(`input[id=buy_ticket_amount]`);

checkbox.addEventListener("change", function () {
  nameInput.disabled = this.checked;
  emailInput.disabled = this.checked;
});

select.addEventListener("change", function () {
  amountInput.value = this.options[this.selectedIndex].dataset.price;
});

select.dispatchEvent(new Event("change"));
