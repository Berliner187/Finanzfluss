function getBondsData(ticker) {

    console.log(ticker);
    google.load("visualization", "1", {packages:["corechart"]});
    google.setOnLoadCallback(drawChart);

    function drawChart() {

        var data = google.visualization.arrayToDataTable([

            ['CMS', 'Сайты на базе систем управления контентом'],
            ['ticker',     60.7],
            ['Joomla',     7.4],
            ['Drupal',     5.1],
            ['Blogger',     2.9],
            ['Magento',     2.8],
            ['TYPO3',     1.6],
            ['PrestaShop',     1.3],
            ['Bitrix',     1.2],
            ['vBulletin',     1.0],
            ['OpenCart',     0.9],
        ]);

        var options = {

        title: 'Самые популярные CMS в 2015 году',
                pieHole: 0.5,
            pieSliceTextStyle: {
            color: 'black',
            },
            legend: 'none'
        };

        var chart = new google.visualization.PieChart(document.getElementById('donut_single'));
        chart.draw(data, options);
    }
}
