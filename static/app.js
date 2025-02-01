document.getElementById('bookingForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const date = document.getElementById('date').value;
    const time = document.getElementById('time').value;
    const people = document.getElementById('people').value;

    const bookingData = {
        name: name,
        date: date,
        time: time,
        people: people
    };

    fetch('/api/booking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(bookingData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            document.getElementById('bookingStatus').innerHTML = `<div class="alert alert-success">${data.message}</div>`;
            loadBookings(); // Ricarica la lista delle prenotazioni
        } else if (data.error) {
            document.getElementById('bookingStatus').innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
        }
    })
    .catch(error => {
        document.getElementById('bookingStatus').innerHTML = `<div class="alert alert-danger">Errore nella comunicazione con il server.</div>`;
    });
});


// Funzione per caricare tutte le prenotazioni esistenti
function loadBookings() {
    fetch('/api/booking')
        .then(response => response.json())
        .then(data => {
            const bookingList = document.getElementById('bookingList');
            bookingList.innerHTML = ''; // Pulisce la lista esistente
            data.forEach(booking => {
                const li = document.createElement('li');
                li.className = 'list-group-item d-flex justify-content-between align-items-center';
                li.innerHTML = `${booking.name} - ${booking.date} ${booking.time} - ${booking.people} persone
                    <button class="btn btn-warning btn-sm" onclick="editBooking(${booking.id})">Modifica</button>
                    <button class="btn btn-danger btn-sm" onclick="cancelBooking(${booking.id})">Cancella</button>`;
                bookingList.appendChild(li);
            });
        })
        .catch(error => {
            console.log('Errore nel caricamento delle prenotazioni', error);
        });
}

// Funzione per modificare una prenotazione
function editBooking(id) {
    const time = prompt('Nuova ora: hh:mm');
    const people = prompt('Nuovo numero di persone:');
    const date = prompt('Nuova data: gg/mm/aaaa');  // Chiedi la data anche

    const updatedBooking = { time, people, date };

    fetch(`/api/booking/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(updatedBooking)
    })
    .then(response => response.json())
    .then(data => {
        if (data.message) {
            alert(data.message);
            loadBookings(); // Ricarica la lista delle prenotazioni
        } else if (data.error) {
            alert(data.error);
        }
    })
    .catch(error => {
        alert('Errore nell\'aggiornamento della prenotazione');
    });
}

// Funzione per cancellare una prenotazione
function cancelBooking(id) {
    if (confirm('Sei sicuro di voler cancellare questa prenotazione?')) {
        fetch(`/api/booking/${id}`, {
            method: 'DELETE',
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                loadBookings(); // Ricarica la lista delle prenotazioni
            }
        })
        .catch(error => {
            alert('Errore nella cancellazione della prenotazione');
        });
    }
}



// Carica le prenotazioni esistenti al caricamento della pagina
loadBookings();
