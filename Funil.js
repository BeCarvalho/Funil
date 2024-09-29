// Definir o ponto de interesse (POI)
var poi = ee.Geometry.Point([-44.60707327403683, -22.561579347225678]);

// Função para mascarar nuvens usando a banda QA60
function maskClouds(image) {
  var cloudBitMask = ee.Number(2).pow(10).int();
  var cirrusBitMask = ee.Number(2).pow(11).int();
  var qa = image.select('QA60');
  var mask = qa.bitwiseAnd(cloudBitMask).eq(0).and(qa.bitwiseAnd(cirrusBitMask).eq(0));
  return image.updateMask(mask);
}

// Função para calcular o NDCI
function calculateNDCI(image) {
  var ndci = image.normalizedDifference(['B5', 'B4']).rename('NDCI');
  return image.addBands(ndci);
}

// Função para calcular o NDWI
function calculateNDWI(image) {
  var ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI');
  return image.addBands(ndwi);
}

// Função para gerar a visualização
function generateVisualization(startDate, endDate) {
  // Carregar coleção de imagens Sentinel-2 SR Harmonized
  var s2Collection = ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
    .filterBounds(poi)
    .filterDate(startDate, endDate)
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) // Filtra imagens com menos de 20% de nuvens
    .map(maskClouds) // Aplica a máscara de nuvens
    .map(calculateNDCI) // Calcula o NDCI
    .map(calculateNDWI); // Calcula o NDWI

  // Média do NDCI e NDWI para o período
  var ndciMean = s2Collection.select('NDCI').mean();
  var ndwiMean = s2Collection.select('NDWI').mean();

  // Máscara de água baseada no NDWI
  var waterMask = ndwiMean.gt(0.2); // Define um limiar para a presença de água

  // Aplicar a máscara no NDCI, mas mantendo o entorno com menor brilho
  var ndciMasked = ndciMean.updateMask(waterMask.multiply(1.0).add(0.0)); // Realça a água e suaviza o entorno

  // Visualização com nova paleta de cores
  var ndciVis = {
    min: -0.03457985482332577,
    max: 0.20368674165667759,
    palette: ['cyan', 'green', 'orange', 'red']
  };

  // Limpar camadas anteriores e adicionar nova camada
  Map.layers().reset();
  Map.centerObject(poi, 13);
  Map.addLayer(ndciMasked.clip(poi.buffer(10000)), ndciVis, 'NDCI Médio (' + startDate + ' a ' + endDate + ')');
}

// Função para criar a legenda
function addLegend(title, palette, labels) {
  // Criar painel da legenda
  var legend = ui.Panel({
    style: {
      position: 'bottom-left',
      padding: '8px 15px'
    }
  });

  // Título da legenda
  var legendTitle = ui.Label({
    value: title,
    style: { fontWeight: 'bold', fontSize: '16px', margin: '0 0 4px 0' }
  });
  
  // Adicionar título ao painel
  legend.add(legendTitle);

  // Cores e valores da legenda
  var makeRow = function(color, name) {
    var colorBox = ui.Label({
      style: {
        backgroundColor: color,
        padding: '8px',
        margin: '0 0 4px 0'
      }
    });
    var description = ui.Label({
      value: name,
      style: { margin: '0 0 4px 6px' }
    });
    return ui.Panel({
      widgets: [colorBox, description],
      layout: ui.Panel.Layout.Flow('horizontal')
    });
  };

  // Adicionar as cores e suas respectivas descrições
  for (var i = 0; i < palette.length; i++) {
    legend.add(makeRow(palette[i], labels[i]));
  }

  // Adicionar legenda ao mapa
  Map.add(legend);
}

// Adicionar legenda com descrições para cyan e red, e sem descrição para as cores intermediárias
addLegend('Concentração de Clorofila (NDCI)', 
          ['cyan', 'green', 'orange', 'red'], 
          ['Baixa concentração', '', '', 'Alta concentração']);

// Interface do app
var panel = ui.Panel({
  style: {
    width: '300px',
    padding: '8px'
  }
});

// Título do app
panel.add(ui.Label({
  value: 'Monitoramento da Concentração de Clorofila (NDCI)',
  style: {
    fontSize: '20px',
    fontWeight: 'bold',
    margin: '10px 5px'
  }
}));

// Widget para selecionar a data inicial
var startDateSlider = ui.DateSlider({
  start: '2021-01-01',
  end: '2024-12-31',
  value: '2023-01-01',
  period: 1,
  onChange: function(dateRange) {
    startDateValue = dateRange.start();
    updateMap();
  },
  style: { width: '250px' }
});
panel.add(ui.Label('Data Inicial'));
panel.add(startDateSlider);

// Widget para selecionar a data final
var endDateSlider = ui.DateSlider({
  start: '2021-01-01',
  end: '2024-12-31',
  value: '2023-12-31',
  period: 1,
  onChange: function(dateRange) {
    endDateValue = dateRange.start();
    updateMap();
  },
  style: { width: '250px' }
});
panel.add(ui.Label('Data Final'));
panel.add(endDateSlider);

// Variáveis para armazenar os valores de data selecionados
var startDateValue = startDateSlider.getValue();
var endDateValue = endDateSlider.getValue();

// Função para atualizar o mapa conforme as datas selecionadas
function updateMap() {
  var formattedStartDate = ee.Date(startDateValue).format('YYYY-MM-dd').getInfo();
  var formattedEndDate = ee.Date(endDateValue).format('YYYY-MM-dd').getInfo();
  
  generateVisualization(formattedStartDate, formattedEndDate);
}

// Inicializar o app com o intervalo padrão
generateVisualization('2023-01-01', '2023-12-31');

// Adicionar o painel à interface
ui.root.insert(0, panel);
