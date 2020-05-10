import React, { useEffect, useState } from 'react';
import { Typography, Card, Tag, Row, Col, message, Space } from 'antd';
import dataMock from './data.json';

function request(): Promise<ResponseType> {
  // return fetch('http://127.0.0.1:8081/api.v1/stock-pool').then(response => response.json()).catch(error => ({code: 500, msg: error.toString()}))
  return fetch('http://62.234.123.212:10001/api/BusinessCate').then(response => dataMock).catch(error => ({code: 500, msg: error.toString()}))
}

interface ResponseType {
  code: number;
  data?: DataType;
  msg: string;
}

interface DataType {
  Date: string;
  StockSet: Array<string>;
  StockName: Array<string>;
  PoolSize: number;
  Rule: string;
}

const App = () => {
  const [dataFetch, setDataFetch] = useState<DataType>({Date: '-', StockSet: [], StockName: [], PoolSize: 0, Rule: '-'})
  const { Date, StockSet, StockName, PoolSize, Rule } = dataFetch

  useEffect(() => {
    (async () => {
      const { code, data, msg } = await request();
      (code === 1001 && data) ? setDataFetch(data) : message.error(msg)
  })();
    
  }, [])

  return (
    <div style={{display: 'flex', justifyContent: 'center', alignItems: 'center', flexDirection: 'column', minHeight: '100vh', background: 'linear-gradient(225deg,#fff,#f0f5ff)', padding: 48}}>
      <div style={{width: '70%'}}>
        <Typography>
          <Typography.Title>股票池</Typography.Title>
          <Typography.Paragraph>时间：{Date}</Typography.Paragraph>
          <Typography.Paragraph>数量：{PoolSize}</Typography.Paragraph>
          <Typography.Paragraph>规则：{Rule}</Typography.Paragraph>
        </Typography>
      </div>
      
      <Card style={{width: '70%', background: '#DEE6F5'}}>
        <Card style={{width: '100%'}}>
          <Row gutter={[16, 24]}>
            {
              StockSet.map((item ,index) => {
                return(
                  <Col>
                    <Tag style={{padding: 24, fontSize: 16, lineHeight: '2'}}>{item}<br/>{StockName[index]}</Tag>
                  </Col>
                );
              })
            }
          </Row>
        </Card>
      </Card>
    </div>
  );
}

export default App;