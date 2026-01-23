document.getElementById("contactForm").addEventListener("submit", function(e) {
    e.preventDefault();

    const name = document.getElementById("name").value;
    const email = document.getElementById("email").value;
    const phone = document.getElementById("phone").value;
    const subject = document.getElementById("subject").value;
    const message = document.getElementById("message").value;

    // Mailto link
    const mailtoLink = mailto: 2 k23it41 @kiot.ac.in ? subject = $ { encodeURIComponent(subject) } & body = Name : $ { encodeURIComponent(name) } % 0 AEmail: $ { encodeURIComponent(email) } % 0 APhone: $ { encodeURIComponent(phone) } % 0 AMessage: $ { encodeURIComponent(message) };

    // Open mail client
    window.location.href = mailtoLink;

    // Show popup after a short delay (to allow mail client to open)
    setTimeout(function() {
        alert('Email sent successfully!');  
    },  500);
});