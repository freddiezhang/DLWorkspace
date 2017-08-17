using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace KustoRetrieve
{
    public class Retrieve
    {
        public static Dictionary<string, Dictionary<string, object>> GetData(string query)
        {
            string url = "https://kusto.aria.microsoft.com";
            string tenantID = "801fc846cce2482cb80e2781803dd9b9";
            string token = "801fc846cce2482cb80e2781803dd9b9-9c5d19aa-51df-481a-88d9-6b09cee45b82-7442";
            var connect = new Kusto.Data.KustoConnectionStringBuilder(url)
            {
                FederatedSecurity = false,
                InitialCatalog = tenantID,
                UserID = tenantID,
                Password = token
            };
            var client = Kusto.Data.Net.Client.KustoClientFactory.CreateCslQueryProvider(connect);
            Dictionary<string, Dictionary<string, object>> machines = new Dictionary<string, Dictionary<string, object>>();
            using (var reader = client.ExecuteQuery(query))
            {
                int columns = reader.FieldCount;
                while (reader.Read())
                {
                    Dictionary<string, object> curr_machine = new Dictionary<string, object>();
                    for (int i = 0; i < columns; i++)
                    {
                        string columnName = reader.GetName(i);
                        var columnValue = reader.GetValue(i);
                        curr_machine.Add(columnName, columnValue);
                    }
                    machines.Add((string) curr_machine["Name"], curr_machine);
                }
                reader.Close();
            }
            return machines;
        }
    }
}
