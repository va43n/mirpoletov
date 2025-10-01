import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, BarChart, Bar, PieChart, Pie, Cell, ResponsiveContainer, AreaChart, Area, ScatterChart, Scatter, RadarChart, Radar, PolarAngleAxis, PolarRadiusAxis, PolarGrid, Text } from "recharts";
import html2canvas from "html2canvas";

import { useInView } from 'react-intersection-observer';

import "./Chart.css"

const Chart = ({ 
  title = "",
  type = "line",
  data = {}
}) => {
  const { ref, inView } = useInView({
    triggerOnce: false,
    rootMargin: '100px 0px',
  });

  const generateColor = (index, total, saturation = 50, lightness = 55, alpha = 1) => {
    return `hsla(${(index * 285 / (total) + 200) % 360}, ${saturation}%, ${lightness}%, ${alpha})`;
  };

  const downloadChartAsPNG = async (event) => {
    const chart = event.target.parentElement.querySelector(".chart-box");

    try {
      const canvas = await html2canvas(chart, {
        backgroundColor: "#ffffff",
        scale: 2,
        useCORS: true,
        logging: false
      });

      const pngImage = canvas.toDataURL("image/png");
      
      const downloadLink = document.createElement("a");
      downloadLink.href = pngImage;
      downloadLink.download = `chart_${new Date().toISOString().split("T")[0]}.png`;
      document.body.appendChild(downloadLink);
      downloadLink.click();
      document.body.removeChild(downloadLink);
    } catch (error) {
      console.log(`Не удалось скачать график: "${error}".`);
    }
  };

  if (type === "line") return (
    <div className="dynamic-container" ref={ref}>
      {inView ? (
        <div className="chart-container">
          <div className="chart-box">
            <ResponsiveContainer width="100%" height={400}>
              <LineChart className="chart" data={data}>
                <CartesianGrid strokeDasharray="3 3" />
                <Text textAnchor="start" x={100} scaleToFit={true} verticalAnchor="start" style={{ fontWeight: "600", fill: "#333" }}>
                  {title}
                </Text>
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip />
                <Legend />
                {Object.keys(data[0])
                .filter(key => key !== "name")
                .map((dataKey, index, array) => (
                  <Line 
                    key={dataKey}
                    type="monotone"
                    dataKey={dataKey}
                    stroke={generateColor(index, array.length)}
                    strokeWidth={3}
                    dot={{ 
                    fill: generateColor(index, array.length),
                    strokeWidth: 2,
                    }}
                    activeDot={{ r: 6 }}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
          <button className="download-button" onClick={downloadChartAsPNG}>
            Скачать PNG
          </button>
        </div>
      ) : (<p>Загрузка</p>)}
    </div>
  );

  if (type === "bar") return (
    <div className="dynamic-container" ref={ref}>
      {inView ? (
    <div className="chart-container">
      <div className="chart-box">
        <ResponsiveContainer width="100%" height={400}>
          <BarChart className="chart" data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <Text textAnchor="start" x={100} scaleToFit={true} verticalAnchor="start" style={{ fontWeight: "600", fill: "#333" }}>
              {title}
            </Text>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(data[0])
            .filter(key => key !== "name")
            .map((dataKey, index, array) => (
              <Bar 
                key={dataKey}
                dataKey={dataKey}
                fill={generateColor(index, array.length)}
                stroke="none"
              />
            ))}
          </BarChart>
        </ResponsiveContainer>
      </div>
      <button className="download-button" onClick={downloadChartAsPNG}>
        Скачать PNG
      </button>
    </div>
    ) : (<p>Загрузка</p>)}
    </div>
  );

  if (type === "pie") return (
    <div className="dynamic-container" ref={ref}>
      {inView ? (
    <div className="chart-container">
      <div className="chart-box">
        <ResponsiveContainer width="100%" height={400}>
          <PieChart>
            <Text textAnchor="start" x={100} scaleToFit={true} verticalAnchor="start" style={{ fontWeight: "600", fill: "#333" }}>
              {title}
            </Text>
            <Pie
              data={data.map(item => ({
                    name: item.name,
                    value: item.num
                  }))}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={150}
              label={({ name }) => `${name}`}
            >
              {data.map(item => ({
                    name: item.name,
                    value: item.num
                  })).map((entry, index) => (
                <Cell 
                  key={`cell-${index}`} 
                  fill={generateColor(index, data.map(item => ({
                    name: item.name,
                    value: item.num
                  })).length)} 
                />
              ))}
            </Pie>
            <Tooltip />
          </PieChart>
        </ResponsiveContainer>
      </div>
      <button className="download-button" onClick={downloadChartAsPNG}>
        Скачать PNG
      </button>
    </div>
    ) : (<p>Загрузка</p>)}
    </div>
  );

  if (type === "area") return (
    <div className="dynamic-container" ref={ref}>
      {inView ? (
    <div className="chart-container">
      <div className="chart-box" >
        <ResponsiveContainer width="100%" height={400}>
          <AreaChart className="chart" data={data}>
            <Text textAnchor="start" x={100} scaleToFit={true} verticalAnchor="start" style={{ fontWeight: "600", fill: "#333" }}>
              {title}
            </Text>
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(data[0])
            .filter(key => key !== "name")
            .map((dataKey, index, array) => (
              <Area 
                key={dataKey}
                type="monotone"
                dataKey={dataKey}
                stroke={generateColor(index, array.length)}
                fill={generateColor(index, array.length)}
                strokeWidth={2}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
      <button className="download-button" onClick={downloadChartAsPNG}>
        Скачать PNG
      </button>
    </div>
    ) : (<p>Загрузка</p>)}
    </div>
  );

  if (type === "radar") return (
    <div className="dynamic-container" ref={ref}>
      {inView ? (
    <div className="chart-container">
      <div className="chart-box">
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={data}>
            <Text textAnchor="start" x={100} scaleToFit={true} verticalAnchor="start" style={{ fontWeight: "600", fill: "#333" }}>
              {title}
            </Text>
            <PolarGrid />
            <PolarAngleAxis dataKey="name" />
            <PolarRadiusAxis angle={360 / data.length + 90} />
            {Object.keys(data[0])
            .filter(key => key !== "name").map((metric, index) => (
              <Radar 
                key={metric}
                name={metric}
                dataKey={metric}
                stroke="none"
                fill={generateColor(index, Object.keys(data[0]).length)}
                fillOpacity={0.6}
              />
            ))}
            <Legend />
            <Tooltip />
          </RadarChart>
        </ResponsiveContainer>
      </div>
      <button className="download-button" onClick={downloadChartAsPNG}>
        Скачать PNG
      </button>
    </div>
    ) : (<p>Загрузка</p>)}
    </div>
  );

  if (type === "scatter") return (
    <div className="dynamic-container" ref={ref}>
      {inView ? (
    <div className="chart-container">
      <div className="chart-box">
        <ResponsiveContainer width="100%" height={400}>
          <ScatterChart className="chart" data={data}>
            <Text textAnchor="start" x={100} scaleToFit={true} verticalAnchor="start" style={{ fontWeight: "600", fill: "#333" }}>
              {title}
            </Text>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="name" />
            <YAxis />
            <Tooltip />
            <Legend />
            {Object.keys(data[0])
            .filter(key => key !== "name")
            .map((dataKey, index, array) => (
              <Scatter 
                key={dataKey}
                name={dataKey}
                dataKey={dataKey}
                fill={generateColor(index, array.length)}
                stroke="none"
              />
            ))}
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <button className="download-button" onClick={downloadChartAsPNG}>
        Скачать PNG
      </button>
    </div>
    ) : (<p>Загрузка</p>)}
    </div>
  );
}

export default Chart;