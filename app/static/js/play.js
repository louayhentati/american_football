// [!!] Bad FileName :)
document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('playForm');
    if (!form) return;

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        const mode = form.dataset.mode; // "edit" or "add"
        const endpoint = (mode === 'edit') ? form.dataset.endpointEdit : form.dataset.endpointAdd;

        const redirectURL = form.dataset.redirect;

        const formData = new FormData(form);

        // Gain/Loss logic
        const gainLoss = parseInt(formData.get('gain_loss')) || 0;
        const currentDown = parseInt(formData.get('down'));
        const currentDistance = parseInt(formData.get('distance'));
        const currentYardLine = parseInt(formData.get('yard_line'));

        let newDown = currentDown;
        let newDistance = currentDistance;
        let newYardLine = currentYardLine + gainLoss;

        if (gainLoss >= currentDistance) {
            newDown = 1;
            newDistance = 10;
        } else if (currentDown < 4) {
            newDown = currentDown + 1;
            newDistance = currentDistance - gainLoss;
        } else {
            // 4th down failure
            newDown = 1;
            newDistance = 10;
            newYardLine = 100 - newYardLine;
        }

        // update form inputs before submit
        const downInputs = document.querySelectorAll('input[name="down"]');
        downInputs.forEach(input => input.checked = parseInt(input.value) === newDown);

        document.querySelector('input[name="distance"]').value = newDistance;
        document.querySelector('input[name="yard_line"]').value = newYardLine;

        fetch(endpoint, {
            method: 'POST', body: new FormData(form),
        })
            .then(response => {
                if (response.ok) {
                    window.location.href = redirectURL;
                } else {
                    response.text().then(text => console.error('Error details:', text));
                }
            })
            .catch(error => console.error('Fetch error:', error));
    });
});

// Utility toggles (unchanged)
function toggleGainLoss() {
    const input = document.querySelector('input[name="gain_loss"]');
    input.value = input.value ? -1 * parseInt(input.value) : '';
}

function toggleYardLine() {
    const input = document.querySelector('input[name="yard_line"]');
    input.value = input.value ? -1 * parseInt(input.value) : '';
}


// Sprint Item: FP-6
document.addEventListener('DOMContentLoaded', function () {
    // handle form submission
    const form = document.querySelector('form');

    form.addEventListener('submit', function (event) {
        event.preventDefault();

        // get form data
        const formData = new FormData(form);

        // add calculated fields
        const gainLoss = parseInt(formData.get('gain_loss')) || 0;
        const currentDown = parseInt(formData.get('down'));
        const currentDistance = parseInt(formData.get('distance'));
        const currentYardLine = parseInt(formData.get('yard_line'));

        // calc new vals
        let newDown = currentDown;
        let newDistance = currentDistance;
        let newYardLine = currentYardLine + gainLoss;

        if (gainLoss >= currentDistance) {
            newDown = 1;
            newDistance = 10;
        } else if (currentDown < 4) {
            newDown = currentDown + 1;
            newDistance = currentDistance - gainLoss;
        } else {
            // 4th down not converted - possession change
            newDown = 1;
            newDistance = 10;
            newYardLine = 100 - newYardLine; // flip field
        }

        // update form fields
        document.querySelector('input[name="down"][value="' + newDown + '"]').checked = true;
        document.querySelector('input[name="distance"]').value = newDistance;
        document.querySelector('input[name="yard_line"]').value = newYardLine;

        // submit the form
        fetch(form.action, {
            method: 'POST', body: new FormData(form),
        })
            .then(response => {
                if (response.ok) {
                    window.location.href = "{{ url_for('drive_detail', drive_id=drive_id) }}";
                } else {
                    console.error('Error saving data');
                }
            });
    });
});
