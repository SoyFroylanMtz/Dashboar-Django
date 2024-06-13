// Initializing datatable
const dataTable = new simpleDatatables.Data("data", {
    searchable: true,
    fixedHeight: true,
    data: {
      headings: ["Video title", "Published Date", "Views Count"],
      data: [
        ["Top 10 VS Code shortcuts", "15-11-2022", "451234"],
        ["Django basics tutorial", "5-09-2021", "451234"],
        ["How to install Python", "12-01-2020", "451234"],
      ]
    }
  });
  