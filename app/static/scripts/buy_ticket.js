let select = document.querySelector(`select[name=kind]`);
let nameInput = document.querySelector(`input[name=full_name]`);
let emailInput = document.querySelector(`input[name=email]`);
let amountSpan = document.querySelector(`div[id=buy_ticket_amount]`);

select.addEventListener("change", function () {
  amountSpan.innerHTML = this.options[this.selectedIndex].dataset.price;
});

select.dispatchEvent(new Event("change"));
