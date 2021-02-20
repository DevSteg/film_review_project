// Materialize Initialization
$(document).ready(function(){
    $('.datepicker').datepicker({
        format: "dd/mm/yyyy", 
        showCleardBtn: true,
        min: new Date(01,01,1920),
        yearRange: [1920,2030]
    });
    $('.sidenav').sidenav({
        edge: "right"
    });
});