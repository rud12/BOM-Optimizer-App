import { useEffect, useMemo, useState } from 'react';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:800';

async function api(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || 'Request failed');
  }
  return res.json();
}

function money(value) {
  return `₹${Number(value || 0).toFixed(2)}`;
}

function App() {
  const path = window.location.pathname;
  const match = path.match(/^\/bom\/(\d+)$/);
  return match ? <BomPage bomId={match[1]} /> : <HomePage />;
}

function HomePage() {
  const [boms, setBoms] = useState([]);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadBoms();
  }, []);

  async function run(action, success) {
    setLoading(true);
    setMessage('');
    try {
      const data = await action();
      if (success) setMessage(success);
      return data;
    } catch (error) {
      setMessage(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function loadBoms() {
    const data = await run(() => api('/api/v1/boms'));
    if (data) setBoms(data);
  }

  async function createBom(event) {
    event.preventDefault();
    if (!name.trim()) return;
    const bom = await run(
      () =>
        api('/api/v1/boms', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name }),
        }),
      'BOM created.'
    );
    if (bom) {
      setName('');
      await loadBoms();
    }
  }

  async function deleteBom(id) {
    if (!window.confirm('Delete this BOM? This cannot be undone.'))
      return;
    await run(() => api(`/api/v1/boms/${id}`, { method: 'DELETE' }), 'BOM deleted.');
    await loadBoms();
  }

  return (
    <main>
      <Header title="BOM Optimizer" loading={loading} />
      {message && <p className="message">{message}</p>}

      <section>
        <h2>Create BOM</h2>
        <form className="row" onSubmit={createBom}>
          <input value={name} onChange={(event) => setName(event.target.value)} placeholder="BOM name" />
          <button>Create</button>
        </form>
      </section>

      <section>
        <h2>Created BOMs</h2>
        {!boms.length && <p>No BOMs created yet.</p>}
        { boms.length && (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Total</th>
                <th>Created</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {boms.map((bom) => (
                <tr key={bom.id}>
                  <td>
                    <a href={`/bom/${bom.id}`}>{bom.name}</a>
                  </td>
                  <td>{money(bom.total_cost)}</td>
                  <td>{new Date(bom.created_at).toLocaleString()}</td>
                  <td>
                    <button type="button" onClick={() => deleteBom(bom.id)}>
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  );
}

function BomPage({ bomId }) {
  const [bom, setBom] = useState(null);
  const [vendors, setVendors] = useState([]);
  const [vendor, setVendor] = useState('all');
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [products, setProducts] = useState([]);
  const [importFile, setImportFile] = useState(null);
  const [qty, setQty] = useState(1);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const selectedVendor = useMemo(
    () => vendors.find((item) => item.name === vendor),
    [vendors, vendor]
  );

  useEffect(() => {
    loadBom();
    loadVendors();
  }, [bomId]);

  useEffect(() => {
    if (!query || query.length < 2 || !vendor || vendor === 'all') {
      setSuggestions([]);
      return;
    }
    const timer = setTimeout(async () => {
      try {
        const data = await api(`/api/v1/vendors/${vendor}/suggestions?q=${encodeURIComponent(query)}`);
        setSuggestions(data);
      } catch {
        setSuggestions([]);
      }
    }, 250);
    return () => clearTimeout(timer);
  }, [query, vendor]);

  async function run(action, success) {
    setLoading(true);
    setMessage('');
    try {
      const data = await action();
      if (success) setMessage(success);
      return data;
    } catch (error) {
      setMessage(error.message);
      return null;
    } finally {
      setLoading(false);
    }
  }

  async function loadBom() {
    const data = await run(() => api(`/api/v1/boms/${bomId}`));
    if (data) setBom(data);
  }

  async function loadVendors() {
    const data = await run(() => api('/api/v1/vendors'));
    if (data) {
      setVendors(data);
    }
  }

  async function searchProducts(event) {
    event.preventDefault();
    if (!query.trim()) return;
    const path =
      vendor === 'all'
        ? `/api/v1/products/search?q=${encodeURIComponent(query)}`
        : `/api/v1/vendors/${vendor}/products?search=${encodeURIComponent(query)}`;
    const data = await run(
      () => api(path),
      'Search complete.'
    );
    if (data) setProducts(data);
  }

  async function addProduct(product) {
	const quantity = Number(qty || 1);
	let minPrice = Infinity;

	for (const p of product.moq) {
		if (p.BreakQuantity <= quantity) {
			minPrice = p.UnitPrice;
		} else {
			break;
		}
	}
	if (minPrice === Infinity) {
		alert('No valid price found for the given quantity.');
		return;
	}

	const unitPrice = minPrice;
    await run(
      () =>
        api(`/api/v1/boms/${bomId}/items`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            component_name: product.component_name,
            alias_name: query.trim() || product.component_name,
            quantity: quantity,
            vendor_name: product.vendor,
            manufacturer: product.manufacturer,
            unit_price: unitPrice,
            stock: product.stock,
            product_url: product.product_url,
          }),
        }),
      'Item added.'
    );
    await loadBom();
  }

  async function deleteItem(itemId) {
    await run(() => api(`/api/v1/boms/${bomId}/items/${itemId}`, { method: 'DELETE' }), 'Item deleted.');
    await loadBom();
  }

  async function importItems(event) {
    event.preventDefault();
    if (!importFile) return;
    const form = new FormData();
    form.append('file', importFile);
    const data = await run(
      () => api(`/api/v1/boms/${bomId}/import`, { method: 'POST', body: form }),
      'File imported into BOM.'
    );
    if (data) {
      setBom(data.bom);
      setImportFile(null);
      if (data.missing_items?.length) {
        window.alert(`Items not found and skipped:\n${data.missing_items.join('\n')}`);
      }
    }
  }

  if (!bom) {
    return (
      <main>
        <Header title="BOM Details" loading={loading} />
        <p>{message || 'Loading...'}</p>
      </main>
    );
  }

  return (
    <main>
      <Header title={bom.name} loading={loading} />
      <p>
        <a href="/">Back to home</a>
      </p>
      {message && <p className="message">{message}</p>}

      <section>
        <h2>Add Item</h2>
        <form className="row" onSubmit={searchProducts}>
          <select value={vendor} onChange={(event) => setVendor(event.target.value)}>
            <option value="all">Search All</option>
            {vendors.map((item) => (
              <option key={item.id} value={item.name}>
                {item.display_name}
              </option>
            ))}
          </select>
          <input
            list="suggestions"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
            placeholder={
              vendor === 'all'
                ? 'Search all vendors'
                : `Search ${selectedVendor?.display_name || 'vendor'} products`
            }
          />
          <datalist id="suggestions">
            {suggestions.map((item) => (
              <option key={item} value={item} />
            ))}
          </datalist>
          <input type="number" min="1" value={qty} onChange={(event) => setQty(event.target.value)} />
          <button>Search</button>
        </form>
        <ProductTable products={products} onAdd={addProduct} />
      </section>

      <section>
        <h2>Import CSV/XLSX</h2>
        <form className="row" onSubmit={importItems}>
          <input
            type="file"
            accept=".csv,.xlsx,.xls"
            onChange={(event) => setImportFile(event.target.files[0])}
          />
          <button>Import into BOM</button>
        </form>
      </section>

      <section>
        <h2>BOM Items</h2>
        <div className="row">
          <strong>Total {money(bom.total_cost)}</strong>
          <a href={`${API_BASE}/api/v1/boms/${bom.id}/export/csv`}>Download CSV</a>
          <a href={`${API_BASE}/api/v1/boms/${bom.id}/export/excel`}>Download Excel</a>
        </div>
        <ItemTable items={bom.items || []} onDelete={deleteItem} />
      </section>
    </main>
  );
}

function Header({ title, loading }) {
  return (
    <header>
      <h1>{title}</h1>
      {loading && <span>Working...</span>}
    </header>
  );
}

function ProductTable({ products, onAdd }) {
  if (!products.length) return <p>No search results.</p>;
  return (
    <table>
      <thead>
        <tr>
          <th>Vendor</th>
          <th>Component</th>
          <th>Manufacturer</th>
          <th>Unit</th>
          <th>Stock</th>
          <th></th>
        </tr>
      </thead>
      <tbody>
        {products.map((product, index) => (
          <tr key={`${product.vendor}-${product.component_name}-${index}`}>
            <td>{product.vendor_display_name}</td>
            <td>
              {product.product_url ? (
                <a href={product.product_url} target="_blank" rel="noreferrer">
                  {product.component_name}
                </a>
              ) : (
                product.component_name
              )}
            </td>
            <td>{product.manufacturer || '-'}</td>
            <td>
				<aside>
					{product.moq.map((moq, index) => (
						<div><div>{moq.BreakQuantity}+</div><div>{money(moq.UnitPrice)}</div></div>
					))}
				</aside>
			</td>
            <td>{product.stock || '-'}</td>
            <td>
              <button type="button" onClick={() => onAdd(product)}>
                Add
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function ItemTable({ items, onDelete }) {
  if (!items.length) return <p>No items.</p>;
  return (
    <table>
      <thead>
        <tr>
          <th>Alias Name</th>
          <th>Component</th>
          <th>Qty</th>
          <th>Vendor</th>
          <th>Manufacturer</th>
          <th>Unit</th>
          <th>Total</th>
          <th>Stock</th>
          {onDelete && <th></th>}
        </tr>
      </thead>
      <tbody>
        {items.map((item) => (
          <tr key={item.id}>
            <td>{item.alias_name || item.component_name}</td>
            <td>
              {item.product_url ? (
                <a href={item.product_url} target="_blank" rel="noreferrer">
                  {item.component_name}
                </a>
              ) : (
                item.component_name
              )}
            </td>
            <td>{item.quantity}</td>
            <td>{item.vendor_display_name || '-'}</td>
            <td>{item.manufacturer || '-'}</td>
            <td>{money(item.unit_price)}</td>
            <td>{money(item.total_price)}</td>
            <td>{item.stock || '-'}</td>
            {onDelete && (
              <td>
                <button type="button" onClick={() => onDelete(item.id)}>
                  Delete
                </button>
              </td>
            )}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default App;
