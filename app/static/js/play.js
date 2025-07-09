// Toggle Gain/Loss sign
function toggleGainLoss() {
    const input = document.querySelector('input[name="gain_loss"]');
    if (input && input.value) {
        input.value = -1 * parseInt(input.value);
    }
}

// Toggle Yard Line sign (Own/Opp)
function toggleYardLine() {
    const input = document.querySelector('input[name="yard_line"]');
    if (input && input.value) {
        input.value = -1 * parseInt(input.value);
    }
}

// Live validation for all numeric fields
document.addEventListener('DOMContentLoaded', () => {
    // Distance validation (1-10)
    const distanceInput = document.getElementById('distance');
    if (distanceInput) {
        distanceInput.addEventListener('input', () => {
            const val = parseInt(distanceInput.value);
            if (isNaN(val) || val < 1 || val > 10) {
                distanceInput.setCustomValidity("Distance must be between 1 and 10 yards.");
            } else {
                distanceInput.setCustomValidity("");
            }
        });
    }

    // Yard Line validation (-49 to 49)
    const yardLineInput = document.getElementById('yard_line');
    if (yardLineInput) {
        yardLineInput.addEventListener('input', () => {
            const val = parseInt(yardLineInput.value);
            if (isNaN(val) || val < -49 || val > 49) {
                yardLineInput.setCustomValidity("Yard line must be between -49 (opponent) and 49 (own).");
            } else {
                yardLineInput.setCustomValidity("");
            }
        });
    }

    // Gain/Loss validation (-99 to 99)
    const gainLossInput = document.getElementById('gain_loss');
    if (gainLossInput) {
        gainLossInput.addEventListener('input', () => {
            const val = parseInt(gainLossInput.value);
            if (isNaN(val) || val < -99 || val > 99) {
                gainLossInput.setCustomValidity("Gain/Loss must be between -99 and 99 yards.");
            } else {
                gainLossInput.setCustomValidity("");
            }
        });
    }
}, {once: true});

// Form submission handler
document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('playForm');
    if (!form) return;

    form.addEventListener('submit', async (event) => {
        event.preventDefault();
        if (form.dataset.submitting === "true") return;
        form.dataset.submitting = "true";

        const formData = new FormData(form);
        const mode = form.dataset.mode;
        const endpoint = mode === 'edit' ? form.dataset.endpointEdit : form.dataset.endpointAdd;
        const redirectURL = form.dataset.redirect;

        try {
            const response = await fetch(endpoint, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                window.location.href = redirectURL;
            } else {
                const text = await response.text();
                console.error("Submission failed:", text);
                alert("There was an error submitting the play. Please try again.");
                form.dataset.submitting = "false";
            }
        } catch (err) {
            console.error("Network error:", err);
            alert("Network error. Check your connection.");
            form.dataset.submitting = "false";
        }
    }, {once: true});
});

// Penalty-Toggle: shows penalty fields only if in result-Radio "Penalty" is selected
document.addEventListener('DOMContentLoaded', function(){
  const penaltyType = document.getElementById('penalty_type');
  const spotFieldContainer = document.getElementById('spot-field-container');
  const penaltySection = document.getElementById('penalty-fields');
  const gainLossInput = document.querySelector('input[name="gain_loss"]');
  if (!penaltySection) return;

  const resultRadios = document.querySelectorAll("input[name='result']");
  //Function that shows the penalty fields block and activates or deactivates the gain_loss field
  function togglePenaltyFields() {
    const sel = document.querySelector("input[name='result']:checked");
    penaltySection.style.display = (sel && sel.value === 'Penalty')
      ? 'block'
      : 'none';
    const isPenalty = (sel && sel.value === 'Penalty');

    if (isPenalty) {//Gain_loss field is deactivated, if Penalty is selected
      gainLossInput.readOnly = true;
      gainLossInput.style.backgroundColor = '#e9ecef';
      gainLossInput.placeholder = "Auto-calculated for penalty";
    } else {
      gainLossInput.readOnly = false;
      gainLossInput.style.backgroundColor = '';
      gainLossInput.placeholder = "";
    }
  }
  penaltyType.addEventListener('change', function() {
   const SHOW_FOR =[
    'Holding (Defense)',  'Illegal Contact','Pass Interference (Defense)','Targeting',
    'Horse-Collar Tackle','Illegal Block in the Back','Chop Block','Facemask', 'Illegal Forward Pass'
    ];

    if (SHOW_FOR.includes(penaltyType.value)) {
        spotFieldContainer.style.display = "block";
    } else {
        spotFieldContainer.style.display = "none";
    }
  });

  //check at every change
  togglePenaltyFields();
  resultRadios.forEach(radio =>radio.addEventListener('change', togglePenaltyFields));
  penaltyType.dispatchEvent(new Event('change'));
});